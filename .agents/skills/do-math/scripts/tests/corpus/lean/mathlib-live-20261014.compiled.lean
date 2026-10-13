import Lean
import Mathlib
theorem lean_smoke_add_zero (n : ℕ) : n + 0 = n := by rfl
theorem lean_smoke_true : True := True.intro

#eval "__DO_MATH_SIGNATURE_BEGIN_lean_smoke_add_zero__"
#check lean_smoke_add_zero
#eval "__DO_MATH_SIGNATURE_END_lean_smoke_add_zero__"
#print axioms lean_smoke_add_zero
#eval "__DO_MATH_SIGNATURE_BEGIN_lean_smoke_true__"
#check lean_smoke_true
#eval "__DO_MATH_SIGNATURE_END_lean_smoke_true__"
#print axioms lean_smoke_true

namespace DoMathDependencyAudit
open Lean
def flatFormat (format : Std.Format) : String := Id.run do
  let mut pending := #[format]
  let mut output := ""
  while !pending.isEmpty do
    let current := pending.back!
    pending := pending.pop
    match current with
    | .nil => pure ()
    | .text text => output := output ++ text
    | .line | .align _ => output := output ++ " "
    | .append left right => pending := pending.push right |>.push left
    | .nest _ inner | .group inner _ | .tag _ inner => pending := pending.push inner
  return output
def scalar [Repr α] (value : α) : Json :=
  Json.mkObj [("atom", toJson (flatFormat (reprArg value)))]
def children : Expr → Array Expr
  | .app fn arg => #[fn, arg]
  | .lam _ type body _ | .forallE _ type body _ => #[type, body]
  | .letE _ type value body _ => #[type, value, body]
  | .mdata _ body | .proj _ _ body => #[body]
  | _ => #[]
def exprEvidence (value : Expr) : CoreM String := do
  let mut ids : ExprStructMap Nat := {}
  let mut nodes : Array Json := #[]
  let mut pending := #[(value, false)]
  while !pending.isEmpty do
    let (current, ready) := pending.back!
    pending := pending.pop
    if (ids.get? ⟨current⟩).isNone then
      if !ready then
        pending := pending.push (current, true)
        for child in (children current).reverse do
          if (ids.get? ⟨child⟩).isNone then pending := pending.push (child, false)
      else
        let refs ← (children current).mapM fun child => do
          let some index := ids.get? ⟨child⟩ | throwError "missing expression child"
          pure (Json.mkObj [("ref", toJson index)])
        let args := match current with
          | .bvar index => #[scalar index]
          | .fvar id => #[scalar id]
          | .mvar id => #[scalar id]
          | .sort level => #[scalar level]
          | .const name levels => #[scalar name, scalar levels]
          | .app _ _ => refs
          | .lam name _ _ info | .forallE name _ _ info => #[scalar name, refs[0]!, refs[1]!, scalar info]
          | .letE name _ _ _ nonDep => #[scalar name, refs[0]!, refs[1]!, refs[2]!, scalar nonDep]
          | .lit literal => #[scalar literal]
          | .mdata data _ => #[scalar data, refs[0]!]
          | .proj name index _ => #[scalar name, scalar index, refs[0]!]
        let index := nodes.size
        nodes := nodes.push (Json.mkObj [("constructor", toJson ("Lean.Expr." ++ current.ctorName)),
          ("args", Json.arr args)])
        ids := ids.insert ⟨current⟩ index
  let some root := ids.get? ⟨value⟩ | throwError "missing expression root"
  return (Json.mkObj [("format", toJson "lean-expr-dag/1"), ("root", toJson root),
    ("nodes", Json.arr nodes)]).compress
def constantEvidence (info : ConstantInfo) : CoreM Json := do
  let type ← exprEvidence info.type
  let value ← match info.value? true with
    | some value => toJson <$> exprEvidence value
    | none => pure Json.null
  return Json.mkObj [("type", toJson type), ("value", value)]
def directRefs (env : Environment) (name : Name) : Except String (Array Name) := do
  let some info := env.checked.get.find? name | throw s!"missing constant {name}"
  let mut refs := info.type.getUsedConstants
  if let some value := info.value? true then
    refs := refs ++ value.getUsedConstants
  if let .inductInfo value := info then
    refs := refs ++ value.ctors.toArray
  return refs
-- The closure of `name`. `known` holds each constant's direct references and is
-- shared by the audited declarations, so every expression is traversed once.
def visit (env : Environment) (name : Name) (known : NameMap (Array Name)) :
    Except String (NameSet × NameMap (Array Name)) := do
  let mut result : NameSet := {}
  let mut known := known
  let mut pending := #[name]
  while !pending.isEmpty do
    let current := pending.back!
    pending := pending.pop
    if !result.contains current then
      result := result.insert current
      let refs ← match known.find? current with
        | some refs => pure refs
        | none => directRefs env current
      known := known.insert current refs
      for ref in refs do
        if !result.contains ref then pending := pending.push ref
  return (result, known)
def audit (name : Name) (emitted : NameSet) (known : NameMap (Array Name)) :
    CoreM (Json × NameSet × NameMap (Array Name)) := do
  let env ← getEnv
  let some info := env.checked.get.find? name | throwError "missing audited declaration"
  let (closure, known) ← match visit env name known with
    | .ok value => pure value
    | .error error => throwError "{error}"
  let names := (closure.toArray.filter (· != name)).qsort Name.lt
  -- The axiom constants of the closure; the verifier compares them with `#print axioms`.
  let axioms := closure.toArray.filter fun constant =>
    match env.checked.get.find? constant with
    | some (.axiomInfo _) => true
    | _ => false
  let mut emitted := emitted
  for dependency in names do
    if !emitted.contains dependency then
      let some constant := env.checked.get.find? dependency | throwError "missing dependency"
      let evidence ← constantEvidence constant
      let row := Json.mkObj [("name", toJson dependency.toString), ("evidence", evidence)]
      IO.println ("__DO_MATH_DEPENDENCY__" ++ row.compress)
      emitted := emitted.insert dependency
  let evidence ← constantEvidence info
  return (Json.mkObj [("declaration", toJson name.toString),
    ("dependencies", toJson (names.map Name.toString)),
    ("axioms", toJson ((axioms.qsort Name.lt).map Name.toString)),
    ("evidence", evidence)], emitted, known)
end DoMathDependencyAudit
elab "#do_math_dependencies " names:ident+ : command => do
  Lean.Elab.Command.liftCoreM do
    let mut emitted : Lean.NameSet := {}
    let mut known : Lean.NameMap (Array Lean.Name) := {}
    for name in names do
      let (evidence, nextEmitted, nextKnown) ← DoMathDependencyAudit.audit name.getId emitted known
      emitted := nextEmitted
      known := nextKnown
      IO.println ("__DO_MATH_DEPENDENCIES__" ++ evidence.compress)

#do_math_dependencies lean_smoke_add_zero lean_smoke_true