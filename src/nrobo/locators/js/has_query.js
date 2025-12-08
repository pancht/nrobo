function findElementsWithDescendant(baseSelector, descendantSelector) {
    const bases = document.querySelectorAll(baseSelector);
    const results = [];

    bases.forEach(base => {
        if (base.querySelector(descendantSelector)) {
            results.push(base);
        }
    });

    return results;
}

return findElementsWithDescendant(arguments[0], arguments[1]);
