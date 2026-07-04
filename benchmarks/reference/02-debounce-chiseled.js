/**
 * Debounce — chiseled version. Closure, no types, no config class.
 */
export function debounce(fn, delay = 300) {
    let timer = null;
    const debounced = (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
    debounced.cancel = () => { clearTimeout(timer); timer = null; };
    return debounced;
}
