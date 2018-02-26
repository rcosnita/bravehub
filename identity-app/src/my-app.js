import {Element as PolymerElement} from "../node_modules/@polymer/polymer/polymer-element.js";

export class MyApp extends PolymerElement {
  static get template() {
    return `
        <div>This is my {{name}} app.</div>

        <h1>{{name}}</h1>
    `;
  }

  static get properties() {
    return {
      "name": {
        "type": String,
      },
    };
  }

  constructor() {
    super();
    this.name = "3.0 preview";
  }

  ready() {
    super.ready();

    setTimeout(() => {
      this.name = "Works as you might expect ...";
    }, 500);
  }
}

customElements.define("my-app", MyApp);
