/** @odoo-module **/

import {Component, markup, useState} from "@odoo/owl";
import {Counter} from "./counter/counter";
import {Card} from "./card/card";
import {TodoList} from "./TodoList/todo_list";

export class Playground extends Component {
    static template = "awesome_owl.playground";
    static components = {Counter, Card, TodoList};

    setup() {
        this.html = markup("<div>Playground</div>");
        this.sum = useState({value: 2});
        // Binding has to be done at the parent component
        // Best is just add the .bind suffix to the prop name in the xml
        this.incrementSum = this.incrementSum.bind(this);
    }

    incrementSum() {
        this.sum.value++;
    }

}
