// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.

/**
 * Webpack configuration for Songo BI Frontend
 */

const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const isDevelopment = process.env.NODE_ENV === 'development';

module.exports = {
  entry: './src/index.tsx',
  
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: isDevelopment ? '[name].js' : '[name].[contenthash].js',
    chunkFilename: isDevelopment ? '[name].chunk.js' : '[name].[contenthash].chunk.js',
    publicPath: '/static/assets/',
    clean: true,
  },

  resolve: {
    extensions: ['.tsx', '.ts', '.js', '.jsx'],
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@/components': path.resolve(__dirname, 'src/components'),
      '@/services': path.resolve(__dirname, 'src/services'),
      '@/utils': path.resolve(__dirname, 'src/utils'),
      '@/types': path.resolve(__dirname, 'src/types'),
      '@/hooks': path.resolve(__dirname, 'src/hooks'),
      '@/store': path.resolve(__dirname, 'src/store'),
    },
  },

  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'ts-loader',
            options: {
              transpileOnly: isDevelopment,
            },
          },
        ],
      },
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              '@babel/preset-env',
              '@babel/preset-react',
              '@babel/preset-typescript',
            ],
          },
        },
      },
      {
        test: /\.css$/,
        use: [
          isDevelopment ? 'style-loader' : MiniCssExtractPlugin.loader,
          'css-loader',
        ],
      },
      {
        test: /\.s[ac]ss$/,
        use: [
          isDevelopment ? 'style-loader' : MiniCssExtractPlugin.loader,
          'css-loader',
          'sass-loader',
        ],
      },
      {
        test: /\.(png|jpe?g|gif|svg)$/,
        type: 'asset/resource',
        generator: {
          filename: 'images/[name].[hash][ext]',
        },
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        type: 'asset/resource',
        generator: {
          filename: 'fonts/[name].[hash][ext]',
        },
      },
    ],
  },

  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
      filename: 'index.html',
      inject: true,
    }),
    
    ...(isDevelopment ? [] : [
      new MiniCssExtractPlugin({
        filename: '[name].[contenthash].css',
        chunkFilename: '[name].[contenthash].chunk.css',
      }),
    ]),
  ],

  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
        antd: {
          test: /[\\/]node_modules[\\/]antd[\\/]/,
          name: 'antd',
          chunks: 'all',
        },
      },
    },
  },

  devServer: {
    port: 9000,
    hot: true,
    historyApiFallback: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8088',
        changeOrigin: true,
      },
      '/login': {
        target: 'http://localhost:8088',
        changeOrigin: true,
      },
      '/logout': {
        target: 'http://localhost:8088',
        changeOrigin: true,
      },
    },
  },

  devtool: isDevelopment ? 'eval-source-map' : 'source-map',
};
