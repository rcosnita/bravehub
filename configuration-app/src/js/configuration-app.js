class ConfigurationApp extends Polymer.Element {
  static get is() { return "configuration-app"; }

  static get properties() {
    return {
      page: {
        type: String,
        reflectToAttribute: true,
        observer: "_pageChanged",
      },
      routeData: Object,
      subroute: String,
      rootPath: String,
    };
  }

  static get observers() {
    return [
      "_routePageChanged(routeData.page)",
    ];
  }

  static get defaultView() { return "configuration-projects-edit-webgl"; }

  _routePageChanged(page) {
    this.page = page || ConfigurationApp.defaultView;

    if (!this.$.drawer.persistent) {
      this.$.drawer.close();
    }
  }

  _pageChanged(page) {
    const resolvedPageUrl = this.resolveUrl(page + ".html");
    Polymer.importHref(
        resolvedPageUrl,
        null,
        this._showPage404.bind(this),
        true);
  }

  _showPage404() {
    this.page = "configuration-view404";
  }
}

window.customElements.define(ConfigurationApp.is, ConfigurationApp);
