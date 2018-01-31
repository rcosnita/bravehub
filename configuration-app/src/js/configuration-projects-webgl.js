"use strict";

import ConfigurationProjectsBasic from "./configuration-projects-base.js";

export default class ConfigurationProjectsWebGl extends ConfigurationProjectsBasic {
  static get is() { return "configuration-projects-webgl"; }

  static get properties() {
    return {
      projectModel: {
        type: Object,
        notify: true,
        value: {},
      },
    };
  }
}

window.customElements.define(ConfigurationProjectsWebGl.is, ConfigurationProjectsWebGl);
