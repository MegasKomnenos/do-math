#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../driver/repeat_cycle.h"

static int deliver(REPEAT_CYCLE *cycle, uint64_t now)
{
    int key = RepeatNext(cycle, now);
    if (key >= 0) RepeatCommit(cycle, key, now);
    return key;
}

int main(void)
{
    REPEAT_CYCLE cycle = {0};
    unsigned char keys[6];
    const unsigned char fb[6] = {0x09, 0x05, 0, 0, 0, 0};
    const unsigned char f1[6] = {0x3A, 0, 0, 0, 0, 0};
    const unsigned char released[6] = {0};
    uint64_t now;
    int key;
    int f1Count = 0;
    int fbCount = 0;

    RepeatKeys(REPEAT_KEY_F, keys);
    assert(memcmp(keys, fb, 6) == 0);
    RepeatKeys(REPEAT_KEY_F1, keys);
    assert(memcmp(keys, f1, 6) == 0);
    RepeatKeys(0, keys);
    assert(memcmp(keys, released, 6) == 0);
    assert(deliver(&cycle, 0) == -1);

    /* Exercise two complete cycles with the real 500 ms controller heartbeat. */
    RepeatConfigure(&cycle, 1, 100, 0);
    for (now = 0; now <= 1400004; now += 2) {
        if (now % 500 == 0) RepeatConfigure(&cycle, 1, 100, now);
        key = deliver(&cycle, now);
        if (now == 200000 || now == 700000 || now == 900000 || now == 1400000) {
            assert(key == REPEAT_KEY_F1);
        }
        if ((now > 200002 && now < 700000) || (now > 900002 && now < 1400000)) {
            assert(key == -1);
        }
        if (key == REPEAT_KEY_F1) ++f1Count;
        if (key == REPEAT_KEY_F) ++fbCount;
    }
    assert(f1Count == 4 && fbCount == 4001);

    /* Heartbeats must not turn a 60 second interval into a 500 ms interval. */
    memset(&cycle, 0, sizeof(cycle));
    RepeatConfigure(&cycle, 1, 60000, 0);
    assert(deliver(&cycle, 0) == REPEAT_KEY_F);
    assert(deliver(&cycle, 2) == 0);
    for (now = 500; now < 60000; now += 500) {
        RepeatConfigure(&cycle, 1, 60000, now);
        assert(deliver(&cycle, now) == -1);
    }
    RepeatConfigure(&cycle, 1, 60000, 60000);
    assert(deliver(&cycle, 60000) == REPEAT_KEY_F);

    /* At a boundary, release F+B before F1; retry undelivered reports. */
    RepeatConfigure(&cycle, 1, 100, 200000);
    assert(deliver(&cycle, 200000) == 0);
    assert(RepeatNext(&cycle, 200002) == REPEAT_KEY_F1);
    assert(RepeatNext(&cycle, 200004) == REPEAT_KEY_F1);
    assert(deliver(&cycle, 200006) == REPEAT_KEY_F1);
    assert(deliver(&cycle, 200008) == 0);
    assert(deliver(&cycle, 200010) == -1);

    /* Manual stop in rest cancels F1; restart begins a fresh active phase. */
    RepeatConfigure(&cycle, 0, 100, 200012);
    assert(deliver(&cycle, 700006) == -1);
    RepeatConfigure(&cycle, 1, 100, 800000);
    assert(cycle.TransitionAt == 1000000);
    assert(deliver(&cycle, 800000) == REPEAT_KEY_F);
    RepeatConfigure(&cycle, 0, 100, 800001);
    assert(deliver(&cycle, 800002) == 0);
    assert(deliver(&cycle, 1000000) == -1);

    /* Controller loss releases a held key and prevents future transitions. */
    RepeatConfigure(&cycle, 1, 100, 1000000);
    assert(deliver(&cycle, 1000000) == REPEAT_KEY_F);
    assert(deliver(&cycle, 1001501) == 0);
    assert(!cycle.Enabled);
    assert(deliver(&cycle, 1200000) == -1);
    RepeatConfigure(&cycle, 1, 100, 1300000);
    RepeatConfigure(&cycle, 1, 100, 1500000);
    assert(deliver(&cycle, 1500000) == REPEAT_KEY_F1);
    assert(deliver(&cycle, 1501501) == 0);
    assert(deliver(&cycle, 2000000) == -1);

    /* Stopping while F1 is held must still deliver its release. */
    RepeatConfigure(&cycle, 1, 10, 2000000);
    RepeatConfigure(&cycle, 1, 10, 2200000);
    assert(deliver(&cycle, 2200000) == REPEAT_KEY_F1);
    RepeatConfigure(&cycle, 0, 10, 2200001);
    assert(deliver(&cycle, 2200002) == 0);
    assert(deliver(&cycle, 2700000) == -1);

    puts("Cycle timing, reports, heartbeat, retry and stop behavior: PASS");
    return 0;
}
