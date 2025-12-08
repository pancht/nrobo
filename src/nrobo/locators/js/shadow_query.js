function queryShadowDeep(selectorList) {
    let nodes = [document];

    for (let selector of selectorList) {
        let nextNodes = [];

        for (let node of nodes) {

            let root = node;
            if (node.shadowRoot) {
                root = node.shadowRoot;
            }

            let found = root.querySelectorAll(selector);

            found.forEach(el => nextNodes.push(el));
        }
        nodes = nextNodes;
    }

    return nodes;
}

return queryShadowDeep(arguments[0]);
