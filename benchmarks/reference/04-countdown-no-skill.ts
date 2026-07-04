/**
 * Countdown timer — no-skill version. Class-based.
 */
export class CountdownTimer {
    #seconds;
    #callback;
    #intervalId = null;
    #onComplete = null;

    constructor(seconds, { onTick, onComplete } = {}) {
        this.#seconds = seconds;
        this.#callback = onTick;
        this.#onComplete = onComplete;
    }

    start() {
        return new Promise((resolve) => {
            console.log(this.#seconds);
            if (this.#callback) this.#callback(this.#seconds);

            this.#intervalId = setInterval(() => {
                this.#seconds--;
                console.log(this.#seconds);
                if (this.#callback) this.#callback(this.#seconds);

                if (this.#seconds <= 0) {
                    clearInterval(this.#intervalId);
                    this.#intervalId = null;
                    if (this.#onComplete) this.#onComplete();
                    resolve();
                }
            }, 1000);
        });
    }

    stop() {
        if (this.#intervalId) {
            clearInterval(this.#intervalId);
            this.#intervalId = null;
        }
    }

    get remaining() {
        return this.#seconds;
    }
}
