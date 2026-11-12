"""Flow and vocabulary fixes for the two docs. Facts unchanged."""
import io, os, sys
root = sys.argv[1]
def apply(path, pairs):
    p = os.path.join(root, path); t = io.open(p, encoding="utf-8").read()
    for old, new in pairs:
        n = t.count(old)
        assert n == 1, (path, n, old[:70])
        t = t.replace(old, new)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)

apply("docs/do-math/first-run-parking-unimodality.md", [
 # 'proposition' -> 'statement' (one word for one object, as in the README)
 ("with the proposition above as its root", "with the statement above as its root"),
 # the two-route overview: say what the four cases split before listing them
 ("The first route splits that failure into four cases around the middle index m = ⌈n/2⌉, by the positions of the descent and the ascent: the descent at the step m−1 into the middle and the ascent at or beyond m; both at or beyond m; the descent below m−1 and the ascent at or beyond m; and both below m. Each case has a reviewed informal proof.",
  "The first route splits that failure into four cases according to where the descent and the later ascent lie relative to the middle index m = ⌈n/2⌉. In the first case the descent is at the step m−1 into the middle and the ascent at or beyond m; in the second both are at or beyond m; in the third the descent is below m−1 and the ascent at or beyond m; in the fourth both are below m. Each case has a reviewed informal proof."),
 # second route: name the property before its formula, and say what follows from it
 ("The second route shows that a conditional log-concavity suffices for the root: if b(n, ℓ) > b(n, ℓ+1) then b(n, ℓ+1)² ≥ b(n, ℓ) b(n, ℓ+2), for all n ≥ 3 and 0 ≤ ℓ ≤ n−3, so that once the sequence has started to decrease it cannot rise again; this condition was then settled at steps at or beyond m and at steps below m separately, and a reviewed relation in record rdc276812 derives the latter from the fourth case of the first route.",
  "The second route shows that a weaker property than unimodality suffices for the root: a log-concavity required only at steps where the sequence has already started to decrease, namely that b(n, ℓ+1)² ≥ b(n, ℓ) b(n, ℓ+2) whenever b(n, ℓ) > b(n, ℓ+1), for all n ≥ 3 and 0 ≤ ℓ ≤ n−3. From this property it follows that once the sequence has started to decrease it cannot rise again, which is unimodality. The property was then settled at steps at or beyond m and at steps below m separately, and a reviewed relation in record rdc276812 derives the second part from the fourth case of the first route."),
 # interrupted sessions: 'fresh' is a system adjective; 'new' says the same in plain English
 ("interrupted peers and reviews are replaced by fresh sessions,", "interrupted peers and reviews are replaced by new sessions,"),
])

apply("docs/do-math/running.md", [
 ("Changing the root's proposition requires a new instance.", "Changing the root's statement requires a new instance."),
 ("containing the exact proposition, for example:", "containing the exact statement, for example:"),
 ("ask the do-math skill to start research on a proposition.", "ask the do-math skill to start research on a statement."),
 ("Interrupted peers, reviews and organizers are replaced by fresh sessions that receive the partial work.",
  "Interrupted peers, reviews and organizers are replaced by new sessions that receive the partial work."),
])
print("docs patched")
