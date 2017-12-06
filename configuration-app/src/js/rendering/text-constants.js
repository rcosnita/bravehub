"use strict";

const FONT_PROPERTIES = {
  "unit": "em",
  "family": "Calibri",
  "fill": "#FFFFFF",
  "align": "left",
  "baseline": "middle",
  "font-weight": "normal",
};

export default class TextConstants {
  static get fontProperties() {
    let fontProperties = {};
    Object.assign(fontProperties, FONT_PROPERTIES);

    return fontProperties;
  }
}
