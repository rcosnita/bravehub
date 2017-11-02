class ConfigurationApiDetails extends Polymer.Element {
  static get properties() {
    return {
      apiSummary: {
        type: Object,
        notify: true,
        observer: "_loadDetails",
      },
      apiModel: {
        type: Object,
        notify: true,
      },
      isNew: {
        type: Boolean,
        notify: true,
      },
      ports: {
        type: String,
        notify: true,
        observer: "_storePorts",
      },
      buildsData: {
        type: String,
        notify: true,
        observer: "_storeBuildsData",
      },
    };
  }
  static get is() { return "configuration-api-details"; }

  _loadDetails(apiSummary) {
    const constants = window.Bravehub.Constants;
    const apiUrl = `${constants.PROJECTS_URL}/${apiSummary.project.id}/apis/${apiSummary.id}`;
    Rx.DOM.ajax({  // eslint-disable-line no-undef
      method: "GET",
      url: apiUrl,
      headers: {
        "Content-Type": "application/json",
      },
      responseType: "json",
    }).subscribe(
      (data) => {
        this.apiModel = data.response;
        this.ports = this.apiModel.exposedPorts.join(",");

        const buildsData = JSON.parse(JSON.stringify(this.apiModel.builds));
        buildsData.forEach((item) => {
          delete item.id;
          delete item.configuration.assets;
          delete item.configuration.droplet;
        });

        this.buildsData = JSON.stringify(buildsData, null, 4);
      },
      (err) => console.log(err)  // eslint-disable-line no-console
    );
  }

  _storeBuildsData(buildsDataStr) {
    const buildsData = JSON.parse(buildsDataStr);
    if (this.isNew) {
      this.apiModel.build = buildsData;
    } else {
      this.apiModel.builds = buildsData;
    }
  }

  _storePorts(exposedPorts) {
    this.apiModel.exposedPorts = exposedPorts.replace(" ").split(",").map((p) => parseInt(p));
  }
}

window.customElements.define(ConfigurationApiDetails.is, ConfigurationApiDetails);
