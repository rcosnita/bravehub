class ConfigurationCreateProjects extends Polymer.Element {
  static get is() { return "configuration-create-projects"; }

  static get properties() {
    return {
      projectModel: {
        type: Object,
        notify: true,
        value: { },
      },
      apiModel: {
        type: Object,
        notify: true,
        value: { },
      },
      configFiles: {
        type: Object,
        notify: true,
        value: { },
      },
      droplet: {
        type: Object,
        notify: true,
      },
    };
  }

  constructor() {
    super();
    this._constants = window.Bravehub.Constants;
  }

  ready() {
    super.ready();
  }

  createProject() {
    const createProject = this._createProject();
    createProject.subscribe(
      (resp) => this._whenProjectCreated(resp),
      (err) => console.log(err)  // eslint-disable-line no-console
    );
  }

  _createProject() {
    return Rx.DOM.ajax({  // eslint-disable-line no-undef
      url: this._constants.PROJECTS_URL,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(this.projectModel),
    });
  }

  _whenProjectCreated(resp) {
    console.log(resp);  // eslint-disable-line no-console
    const projectUrl = resp.xhr.getResponseHeader("Location");

    this._createApi(projectUrl).subscribe(
      (resp) => this._whenApiCreated(resp),
      (err) => console.log(err)  // eslint-disable-line no-console
    );
  }

  _createApi(projectUrl) {
    return Rx.DOM.ajax({  // eslint-disable-line no-undef
      url: `${projectUrl}/apis`,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(this.apiModel),
    });
  }

  _whenApiCreated(resp) {
    console.log(resp);  // eslint-disable-line no-console
    const apiUrl = resp.xhr.getResponseHeader("Location");

    this._uploadDroplet(apiUrl);
    this._uploadConfigFiles(apiUrl);
  }

  _uploadDroplet(apiUrl) {
    if (!this.droplet) {
      return;
    }

    Rx.DOM.ajax({  // eslint-disable-line no-undef
      url: `${apiUrl}/builds/1`,
      method: "PUT",
      body: this.droplet,
      headers: {
        "Content-Type": "application/vnd.bravehub.droplet-binary",
      },
    }).subscribe(
      (resp) => console.log(resp),  // eslint-disable-line no-console
      (err) => console.log(err)  // eslint-disable-line no-console
    );
  }

  _uploadConfigFiles(apiUrl) {
    Object.keys(this.configFiles).forEach((fName) => {
      const file = this.configFiles[fName];

      Rx.DOM.ajax({  // eslint-disable-line no-undef
        url: `${apiUrl}/builds/1/configassets`,
        method: "POST",
        body: file,
        headers: {
          "Content-Type": "application/vnd.bravehub.configurationasset-binary",
          "X-ConfigAsset-MountPath": `/${fName}`,
        },
      }).subscribe(
        (resp) => console.log(resp),  // eslint-disable-line no-console
        (err) => console.log(err)  // eslint-disable-line no-console
      );
    });
  }
}

window.customElements.define(ConfigurationCreateProjects.is, ConfigurationCreateProjects);
