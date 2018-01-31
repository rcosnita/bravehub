"use strict";

import {Model} from "./shape-model.js";

export default class ApiModel extends Model {
  constructor(data) {
    super(data);
    this._constants = window.Bravehub.Constants;
  }

  fetch(opts) {
    const id = opts.id;
    const projectId = opts.projectId;

    if (!id) {
      console.info("API shape does not have an unique identifier associated.");
      return;
    }

    return new Promise((resolve, reject) => {
      const action = Rx.DOM.ajax({  // eslint-disable-line no-undef
        url: `${this._constants.PROJECTS_URL}/${projectId}/apis/${id}`,
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      action.subscribe(
        (resp) => {
          Object.assign(this, JSON.parse(resp.response));
          resolve(this);
        },
        (err) => console.log(err)  // eslint-disable-line no-console
      );
    });
  }
}
