class ConfigurationUploadFile extends Polymer.Element {
  static get is() { return "configuration-upload-file"; }

  static get properties() {
    return {
      archive: Boolean,
      archiveResult: {
        type: Object,
        notify: true,
      },
      folderUpload: Boolean,
      filesContent: {
        type: Object,
        notify: true,
        value: { },
      },
      label: String,
    };
  }

  constructor() {
    super();
    this._files = [];
    this._tar = undefined;
  }

  _selectFolder(event) {
    this._files = [];

    for(let idx = 0; idx < event.target.files.length; idx++) {
      const f = event.target.files[idx];
      this._files.push(f);
    }

    if (this.archive) {
      this._createTarArchive();
      return;
    }

    this._indexFiles();
  }

  _isAllowed(path) {
    return !path.startsWith("\.");
  }

  _removeFirstFolder(path) {
    return path.substr(path.split("/")[0].length + 1);
  }

  _filterFiles(callback, trimFirstLevel) {
    trimFirstLevel = trimFirstLevel === undefined ? true : trimFirstLevel;
    this._files.forEach((f) => {
      if (!this._isAllowed(f.name)) {
        return;
      }

      const fPath = f.webkitRelativePath;
      const fName = trimFirstLevel ? this._removeFirstFolder(fPath) : fPath;
      callback.call(this, fName, f);
    });
  }

  _createTarArchive() {
    this._tar = new tarball.TarWriter();  // eslint-disable-line no-undef
    this._filterFiles((fName, f) => this._tar.addFile(fName, f));

    this._tar.write().then((blob) => this.archiveResult = blob);
  }

  _indexFiles() {
    this._filterFiles((fName, f) => {
      this.filesContent[fName] = f;
    }, false);
  }
}

window.customElements.define(ConfigurationUploadFile.is, ConfigurationUploadFile);
