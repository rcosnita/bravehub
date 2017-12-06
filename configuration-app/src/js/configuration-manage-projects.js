"use strict";
class ConfigurationManageProjects extends Polymer.Element {
  static get is() { return "configuration-manage-projects"; }

  static get properties() {
    return {
      projects: Array,
      selectedProject: {
        type: Object,
        notify: true,
        observer: "_displayProject",
      },
      projectApis: Array,
    };
  }

  constructor() {
    super();
    this._constants = window.Bravehub.Constants;
  }

  ready() {
    super.ready();
    this._loadProjects();
  }

  _loadProjects() {
    Rx.DOM.ajax({  // eslint-disable-line no-undef
      method: "GET",
      url: this._constants.PROJECTS_URL,
      headers: {
        "Content-Type": "application/json",
      },
      responseType: "json",
    })
      .map((data) => data.response.items)
      .map((projects) => projects.filter((p) => p.owner.id === "3746656e-c319-447f-9fc1-2f85f1cbcd33"))
      .subscribe(
        (projects) => {
          this.setProperties({projects: projects});
        },
        (err) => console.log(err)  // eslint-disable-line no-console
      );
  }

  _fetchProjectApis(projectId) {
    const apiUrl = `${this._constants.PROJECTS_URL}/${projectId}/apis`;

    return Rx.DOM.ajax({  // eslint-disable-line no-undef
      method: "GET",
      url: apiUrl,
      headers: {
        "Content-Type": "application/json",
      },
      responseType: "json",
    });
  }

  _displayApis(apisLoader) {
    apisLoader.subscribe(
      (data) => {
        const apis = data.response.items;
        this.setProperties({projectApis: apis});
      },
      (err) => console.log(err)  // eslint-disable-line no-console
    );
  }

  _displayProject(item) {
    if (!item) {
      return;
    }

    const projectId = item.value;

    Rx.Observable.from(this.projects)  // eslint-disable-line no-undef
        .filter((p) => p.id = projectId)
        .map((p) => this._fetchProjectApis(p.id))
        .subscribe(
          (apisLoader) => this._displayApis(apisLoader),
          (err) => console.log(err)  // eslint-disable-line no-console
        );
  }
}

window.customElements.define(ConfigurationManageProjects.is, ConfigurationManageProjects);
