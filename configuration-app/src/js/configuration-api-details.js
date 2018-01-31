"use strict";

import {Events, UiEvent} from "./events/events.js";

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
        observer: "_restoreModel",
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
      projectModel: Object,
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
    this._projectModel = undefined;
  }

  static get is() { return "configuration-api-details"; }

  _isModelNew() {
    return this.apiModel && !this.apiModel.id;
  }

  createApi() {
    // TODO (rcosnita) add support for update operations.
    const projectLocation = this.projectModel.__meta__.location;

    const action = Rx.DOM.ajax({  // eslint-disable-line no-undef
      url: `${projectLocation}/apis`,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(this.apiModel),
    });

    action.subscribe(
      (resp) => this._whenApiCreated(resp),
      (err) => console.log(err)  // eslint-disable-line no-console
    );
  }

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
        Object.assign(this.apiModel, data.response);
        this._restoreModel(this.apiModel);
      },
      (err) => console.log(err)  // eslint-disable-line no-console
    );
  }

  _restoreModel(apiModel) {
    this.apiModel = apiModel;
    this.isNew = this._isModelNew();

    if (!apiModel || JSON.stringify(apiModel) === "{}") {
      return;
    }

    const exposedPorts = (apiModel.exposedPorts || [80]).join(",");
    const buildsData = this._isModelNew() ? apiModel.build : apiModel.builds;
    this.buildsData = JSON.stringify(buildsData || {});
    this._storeBuildsData(this.buildsData);

    this.ports = exposedPorts;
    this._storePorts(exposedPorts);
  }

  _storeBuildsData(buildsDataStr) {
    let buildsData = { };

    try {
      buildsData = JSON.parse(buildsDataStr);
    } catch (err) {
      // suppress invalid json error in here. The user might be typing builds data.
    }

    if (this._isModelNew()) {
      this.apiModel.build = buildsData;
    } else {
      this.apiModel.builds = buildsData;
    }
  }

  _storePorts(exposedPorts) {
    this.apiModel.exposedPorts = exposedPorts.replace(" ").split(",").map((p) => parseInt(p));
  }

  _whenApiCreated(resp) {
    const apiLocation = resp.xhr.getResponseHeader("Location");
    const tmp = apiLocation.split("/");
    const apiId = tmp[tmp.length - 1];

    this.apiModel.id = apiId;

    const invalidateEvtName = Events.sceneGraph.INVALIDATE_SCENE;
    this.messageBus.emit(invalidateEvtName, new UiEvent(invalidateEvtName, {
      "node": this,
    }));

    this._configUploaded = false;
    this._dropletUploaded = false;

    this._uploadDroplet(apiLocation);
    this._uploadConfigFiles(apiLocation);
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
      (resp) => {
        this._dropletUploaded = true;
        this._whenBinariesUploaded();
      },
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
        (resp) => {
          this._configUploaded = true;
          this._whenBinariesUploaded();
        },
        (err) => console.log(err)  // eslint-disable-line no-console
      );
    });
  }

  _whenBinariesUploaded() {
    if (!this._configUploaded || !this._dropletUploaded) {
      return;
    }

    this._configUploaded = false;
    this._dropletUploaded = false;

    this._loadDetails({
      id: this.apiModel.id,
      project: this.projectModel,
    });

    alert("API created successfully ...");

    const evtName = Events.gestures.CLOSE_EDITOR;
    this.messageBus.emit(evtName, new UiEvent(evtName, {
      "node": this,
    }));
  }
}

window.customElements.define(ConfigurationApiDetails.is, ConfigurationApiDetails);
