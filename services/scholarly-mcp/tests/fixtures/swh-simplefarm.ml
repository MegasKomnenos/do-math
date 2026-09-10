(* program computing a function over a stream of floats ... 
   by using a farm (very simple!) *)

let farm_worker x =
  x *. x;;

let nothing _ = ();;

let generate_input_stream =
  let x = ref 0.0 in
  (function () -> 
    begin
      x := !x +. 1.0;
      if(!x < 10.0) then !x else raise End_of_file
    end);;

let print_result x =
  print_float x; print_newline();;

let program ()= 
  startstop
    (generate_input_stream, nothing)
    (print_result,nothing,nothing)
    (farm(seq(farm_worker),4))
in
  pardo program
;;
