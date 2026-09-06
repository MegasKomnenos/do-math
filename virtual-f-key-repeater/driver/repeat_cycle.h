/* Timing and report selection shared by the driver and its native tests. */
#ifndef VIRTUAL_F_REPEAT_CYCLE_H
#define VIRTUAL_F_REPEAT_CYCLE_H

#include <stdint.h>

#define REPEAT_ACTIVE_MS 200000ULL
#define REPEAT_REST_MS   500000ULL
#define REPEAT_WATCHDOG_MS 1500ULL

#define REPEAT_KEY_F  0x09
#define REPEAT_KEY_B  0x05
#define REPEAT_KEY_F1 0x3A

typedef struct _REPEAT_CYCLE {
    int Enabled;
    int Resting;
    unsigned int IntervalMs;
    unsigned char KeyDown;
    uint64_t LastControlAt;
    uint64_t NextPressAt;
    uint64_t TransitionAt;
} REPEAT_CYCLE;

static void RepeatConfigure(REPEAT_CYCLE *cycle, int enabled,
                            unsigned int intervalMs, uint64_t now)
{
    if (enabled && !cycle->Enabled) {
        cycle->Resting = 0;
        cycle->NextPressAt = now;
        cycle->TransitionAt = now + REPEAT_ACTIVE_MS;
    }
    cycle->Enabled = enabled;
    cycle->IntervalMs = intervalMs;
    cycle->LastControlAt = now;
}

/* Returns -1 when no report is due, 0 for release, or a key usage for press.
 * Selection does not consume a report: commit only after successful delivery. */
static int RepeatNext(REPEAT_CYCLE *cycle, uint64_t now)
{
    if (cycle->Enabled && now - cycle->LastControlAt > REPEAT_WATCHDOG_MS) {
        cycle->Enabled = 0;
    }
    if (cycle->KeyDown) {
        return 0;
    }
    if (!cycle->Enabled) {
        return -1;
    }
    if (now >= cycle->TransitionAt) {
        return REPEAT_KEY_F1;
    }
    if (!cycle->Resting && now >= cycle->NextPressAt) {
        return REPEAT_KEY_F;
    }
    return -1;
}

static void RepeatCommit(REPEAT_CYCLE *cycle, int key, uint64_t now)
{
    cycle->KeyDown = (unsigned char)key;
    if (key == REPEAT_KEY_F1) {
        cycle->Resting = !cycle->Resting;
        cycle->TransitionAt = now +
            (cycle->Resting ? REPEAT_REST_MS : REPEAT_ACTIVE_MS);
        cycle->NextPressAt = now;
    }
    else if (key == REPEAT_KEY_F) {
        cycle->NextPressAt = now + cycle->IntervalMs;
    }
}

static void RepeatKeys(unsigned char key, unsigned char keys[6])
{
    keys[0] = key;
    keys[1] = key == REPEAT_KEY_F ? REPEAT_KEY_B : 0;
    keys[2] = keys[3] = keys[4] = keys[5] = 0;
}

#endif
