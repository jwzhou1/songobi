// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.

/**
 * Theme configuration for Songo BI
 */

import { ThemeConfig } from 'antd';

export const songoTheme: ThemeConfig = {
  token: {
    // Primary colors
    colorPrimary: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    colorInfo: '#1890ff',
    
    // Layout
    borderRadius: 6,
    wireframe: false,
    
    // Typography
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    fontSize: 14,
    fontSizeHeading1: 38,
    fontSizeHeading2: 30,
    fontSizeHeading3: 24,
    fontSizeHeading4: 20,
    fontSizeHeading5: 16,
    
    // Spacing
    padding: 16,
    margin: 16,
    
    // Colors
    colorBgContainer: '#ffffff',
    colorBgElevated: '#ffffff',
    colorBgLayout: '#f5f5f5',
    colorBgSpotlight: '#ffffff',
    colorBorder: '#d9d9d9',
    colorBorderSecondary: '#f0f0f0',
    
    // Text colors
    colorText: '#000000d9',
    colorTextSecondary: '#00000073',
    colorTextTertiary: '#00000040',
    colorTextQuaternary: '#00000026',
  },
  
  components: {
    Layout: {
      headerBg: '#001529',
      headerColor: '#ffffff',
      siderBg: '#001529',
      triggerBg: '#002140',
      triggerColor: '#ffffff',
    },
    
    Menu: {
      darkItemBg: '#001529',
      darkItemColor: '#ffffff',
      darkItemHoverBg: '#1890ff',
      darkItemSelectedBg: '#1890ff',
      darkSubMenuItemBg: '#000c17',
    },
    
    Button: {
      borderRadius: 6,
      controlHeight: 32,
    },
    
    Card: {
      borderRadius: 8,
      paddingLG: 24,
    },
    
    Table: {
      borderRadius: 6,
      headerBg: '#fafafa',
    },
    
    Drawer: {
      zIndexPopup: 1001,
    },
    
    Modal: {
      borderRadius: 8,
    },
  },
};

export const darkTheme: ThemeConfig = {
  ...songoTheme,
  token: {
    ...songoTheme.token,
    colorBgContainer: '#141414',
    colorBgElevated: '#1f1f1f',
    colorBgLayout: '#000000',
    colorText: '#ffffffd9',
    colorTextSecondary: '#ffffff73',
    colorBorder: '#434343',
    colorBorderSecondary: '#303030',
  },
};
