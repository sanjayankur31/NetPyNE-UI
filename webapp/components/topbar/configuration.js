import React from 'react';
import { bgRegular, bgDark, font, primaryColor, gutter, radius } from '../../theme'

import { openTopbarDialog, changePageTransitionMode } from '../../redux/actions/topbar'
import { openDialog } from '../../redux/actions/general'
import { TOPBAR_CONSTANTS } from '../../constants'


const style = {
  standard: {
    background: bgRegular,
    borderRadius: 0,
    border: 0,
    boxShadow: '0px 0px',
    color: '#ffffff',
    paddingLeft: 30,
    paddingRight: 30,
    fontSize: 16,
    fontWeight: 400,
    fontFamily: font,
    margin: '0px 0px 0px 0px',
    height: '100%',
    borderLeft: 0,
    borderRight: 0,
    borderBottom: 0,
    textTransform: 'capitalize',
    textAlign: 'left',
    justifyContent: 'start',

    'hr': {}

  },
  lighter: { background: primaryColor },
  padding: {
    fontSize: 16,
    paddingTop: `calc(${gutter} / 2)`,
    paddingBottom: `calc(${gutter} / 2)`
  }

}

const topLevelMenuItemStyle = {
  standard: {
    paddingLeft: `calc(${gutter} / 2)`,
    paddingRight: `calc(${gutter} / 2)`,
    background: bgDark,
  },
  hover: {
    paddingLeft: `calc(${gutter} / 2)`,
    paddingRight: `calc(${gutter} / 2)`,
    background: '#202020',
  },
};


export default {
  global: {
    color: "white",
    subMenuOpenOnHover: true,
    menuOpenOnClick: true,
    menuPadding: 0,
    fontFamily: font,
    menuFontSize: "14",
    subMenuFontSize: "12",
    background: bgRegular,
    buttonsStyle: {
      standard: style.standard,
      hover: {
        ...style.standard,
        ...style.lighter
      }
    },
    labelsStyle: {
      standard: { ...style.padding, },
      hover: {
        ...style.lighter,
        ...style.padding
      }
    },
    drawersStyle: {
      standard: {
        top: 10,
        backgroundColor: bgDark,
        borderRadius: 0,
        color: '#ffffff',
        fontSize: 14,
        fontFamily: font,
        minWidth: 110,
        borderLeft: 0,
        borderRight: 0,
        borderBottom: 0,
        borderBottomLeftRadius: radius,
        borderBottomRightRadius: radius,
      }
    },
  },
  itemOptions: { customArrow: <i className="fa fa-caret-right menu-caret" /> },
  buttons: [
    {
      label: "NetPyNE",
      position: "bottom-start",
      icon: "",
      list: [
        {
          label: "About...",
          icon: "",
          action: {
            handlerAction: "redux",
            parameters: [openDialog, { title: "About", message: "This is about tab" }]
          }
        },
        {
          label: "Contribute",
          icon: "",
          action: {
            handlerAction: "redux",
            parameters: [openDialog, { title: "Contribute", message: "This is Contribute tab" }]
          }
        },
      ],
      styles: topLevelMenuItemStyle
    },
    {
      label: "File",
      position: "bottom-start",
      icon: "",
      styles: topLevelMenuItemStyle,
      list: [
        {
          label: "New",
          icon: "",
          list: [
            {
              label: "Blank",
              icon: "",
              action: {
                handlerAction: "redux",
                parameters: [openTopbarDialog, TOPBAR_CONSTANTS.NEW_MODEL]
              }
            }
          ]
        },
        {
          label: "Open",
          icon: "",
          action: {
            handlerAction: 'redux',
            parameters: [openTopbarDialog, TOPBAR_CONSTANTS.LOAD]
          }
        },
        {
          label: "Save",
          icon: "",
          action: {
            handlerAction: 'redux',
            parameters: [openTopbarDialog, TOPBAR_CONSTANTS.SAVE]
          }
        },
        {
          label: "Import...",
          icon: "",
          list: [
            {
              label: "From python...",
              icon: "",
              action: {
                handlerAction: "redux",
                parameters: [openTopbarDialog, TOPBAR_CONSTANTS.IMPORT_HLS]
              }
            },
            {
              label: "From cell template...",
              icon: "",
              action: {
                handlerAction: "redux",
                parameters: [openTopbarDialog, TOPBAR_CONSTANTS.IMPORT_CELL_TEMPLATE]
              }
            }
          ]
        },
        {
          label: "Export...",
          icon: "",
          list: [
            {
              label: "To python...",
              icon: "",
              action: {
                handlerAction: 'redux',
                parameters: [openTopbarDialog, TOPBAR_CONSTANTS.EXPORT_HLS]
              }
            },
          ]
        },
        {
          label: "Resources...",
          icon: "",
          list: [
            {
              label: "Upload...",
              icon: "",
              action: {
                handlerAction: "redux",
                parameters: [openTopbarDialog, TOPBAR_CONSTANTS.UPLOAD_FILES]
              }
            },
            {
              label: "Download...",
              icon: "",
              action: {
                handlerAction: "redux",
                parameters: [openTopbarDialog, TOPBAR_CONSTANTS.DOWNLOAD_FILES]
              }
            }
          ]
        },
      ]
    },
    {
      label: "Model",
      icon: "",
      position: "bottom-start",
      styles: topLevelMenuItemStyle,
      list: [
        {
          label: TOPBAR_CONSTANTS.CREATE_NETWORK,
          icon: "",
          action: {
            handlerAction: "redux",
            parameters: [changePageTransitionMode, TOPBAR_CONSTANTS.CREATE_NETWORK]
          }
        },
        {
          label: TOPBAR_CONSTANTS.CREATE_AND_SIMULATE_NETWORK,
          icon: "",
          action: {
            handlerAction: "redux",
            parameters: [changePageTransitionMode, TOPBAR_CONSTANTS.CREATE_AND_SIMULATE_NETWORK]
          }
        },
        {
          label: TOPBAR_CONSTANTS.EXPLORE_EXISTING_NETWORK,
          icon: "",
          action: {
            handlerAction: "redux",
            parameters: [changePageTransitionMode, TOPBAR_CONSTANTS.EXPLORE_EXISTING_NETWORK]
          }
        },
      ]
    },
    {
      label: "Help",
      icon: "",
      styles: topLevelMenuItemStyle,
      action: {
        handlerAction: '',
        parameters: []
      }
    },
  ]
}