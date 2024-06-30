/** @odoo-module **/

import {Component, useState, useRef} from "@odoo/owl";
import {TodoItem} from "./todo_item";
import {useAutofocus} from "../utils";

export class TodoList extends Component {
    static template = "awesome_owl.todo_list";
    static components = {TodoItem};

    setup() {
        this.todos = useState([]);
        useAutofocus("todoInput");
    }

    addTodo(event) {
        if (event.keyCode === 13 && event.target.value !== "") {
            this.todos.push({
                id: this.todos.length,
                description: event.target.value,
                isCompleted: false,
            });
            event.target.value = "";
        }
    }

    toggleTodo(todoId) {
        const todo = this.todos.find(todo => todo.id === todoId);
        if (todo) {
            todo.isCompleted = !todo.isCompleted;
        }
    }

    deleteTodo(todoId) {
        const index = this.todos.findIndex(todo => todo.id === todoId);
        if (index >= 0) {
            console.log("Removing");
            this.todos.splice(index, 1);
        }
    }

}