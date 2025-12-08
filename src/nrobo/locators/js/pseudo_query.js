function matchPseudo(el, pseudo) {

    if (pseudo === ":visible") {
        return !!( el.offsetWidth || el.offsetHeight || el.getClientRects().length );
    }

    if (pseudo === ":hidden") {
        return !( el.offsetWidth || el.offsetHeight || el.getClientRects().length );
    }

    if (pseudo === ":enabled") {
        return !el.disabled;
    }

    if (pseudo === ":disabled") {
        return !!el.disabled;
    }

    if (pseudo === ":checked") {
        return !!el.checked;
    }

    if (pseudo.startsWith(":not(")) {
        const sel = pseudo.slice(5, -1);
        return !el.matches(sel);
    }

    return true; // fallback
}

function queryPseudo(baseSelector, pseudos) {
    const nodes = Array.from(document.querySelectorAll(baseSelector));
    const results = [];

    nodes.forEach(el => {
        let ok = true;

        for (let pseudo of pseudos) {
            if (!matchPseudo(el, pseudo)) {
                ok = false;
                break;
            }
        }

        if (ok) results.push(el);
    });

    return results;
}

return queryPseudo(arguments[0], arguments[1]);
