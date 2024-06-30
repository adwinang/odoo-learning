/** @odoo-module */

import {useRef, onMounted} from "@odoo/owl";

/**
 * @param refName {string}
 */
export function useAutofocus(refName) {
    const ref = useRef(refName);
    onMounted(() => {
        ref.el.focus();
    })
}
