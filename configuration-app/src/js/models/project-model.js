"use strict";

import {Model} from "./shape-model.js";

export default class ProjectModel extends Model {
  constructor(data) {
    super(data);
    this._constants = window.Bravehub.Constants;
  }

  fetch(opts) {
    const id = opts.id;
    const projectLocation = `${this._constants.PROJECTS_URL}/${id}`;

    return new Promise((resolve, reject) => {
      const action = Rx.DOM.ajax({  // eslint-disable-line no-undef
        url: projectLocation,
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      action.subscribe(
        (resp) => {
          Object.assign(this, JSON.parse(resp.response));
          this.__meta__ = {"location": projectLocation};
          resolve(this);
        },
        (err) => console.log(err)  // eslint-disable-line no-console
      );
    });
  }
}
