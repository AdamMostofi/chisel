/**
 * Countdown timer — chiseled version.
 */
export function countdown(seconds, onTick) {
    const tick = () => {
        console.log(seconds);
        if (onTick) onTick(seconds);
        if (seconds-- <= 0) return;
        setTimeout(tick, 1000);
    };
    tick();
}
