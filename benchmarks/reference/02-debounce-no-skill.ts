/**
 * Debounce — no-skill version. Class-based, over-abstracted.
 */
export class DebounceConfig {
    constructor({ delay = 300, leading = false, trailing = true } = {}) {
        this.delay = delay;
        this.leading = leading;
        this.trailing = trailing;
    }
}

export interface DebouncedFunction<T extends (...args: any[]) => any> {
    (...args: Parameters<T>): ReturnType<T> | undefined;
    cancel(): void;
    flush(): ReturnType<T> | undefined;
}

export function debounce<T extends (...args: any[]) => any>(
    fn: T,
    configOrDelay: DebounceConfig | number = 300
): DebouncedFunction<T> {
    const config = configOrDelay instanceof DebounceConfig
        ? configOrDelay
        : new DebounceConfig({ delay: configOrDelay });

    let timer: ReturnType<typeof setTimeout> | null = null;
    let lastArgs: Parameters<T> | null = null;
    let lastContext: any = null;

    const debounced = function (this: any, ...args: Parameters<T>): ReturnType<T> | undefined {
        lastContext = this;
        lastArgs = args;

        if (config.leading && !timer) {
            const result = fn.apply(this, args);
            timer = setTimeout(() => { timer = null; }, config.delay);
            return result;
        }

        if (timer) clearTimeout(timer);
        timer = setTimeout(() => {
            timer = null;
            if (config.trailing && lastArgs) {
                fn.apply(lastContext, lastArgs);
                lastArgs = null;
            }
        }, config.delay);
        return undefined;
    };

    debounced.cancel = () => {
        if (timer) clearTimeout(timer);
        timer = null;
        lastArgs = null;
    };

    debounced.flush = () => {
        if (timer && lastArgs) {
            clearTimeout(timer);
            timer = null;
            return fn.apply(lastContext, lastArgs);
        }
        return undefined;
    };

    return debounced;
}
