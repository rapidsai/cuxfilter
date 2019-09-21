const path = require('path');
const webpack = require('webpack');
const HTMLWebpackPlugin = require('html-webpack-plugin');
const uglifyJsPlugin = require('uglifyjs-webpack-plugin');
module.exports = {
    entry: './src/index.js',
    output: {
        library: 'cuXfilter',
        libraryTarget: 'umd',
        libraryExport: 'default',
        path: path.resolve(__dirname, '../dist'),
        filename: 'cuXfilter-client.js'
    },
    mode: 'production',
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: ['babel-loader']
            },
            {
                test: /\.scss$/,
                use: [
                    'style-loader', 
                    'css-loader', 
                    'postcss-loader', 
                    'sass-loader'
                ]
            }
        ]
    },
    plugins: [
        new uglifyJsPlugin(),
        // new HTMLWebpackPlugin({
        //     template: path.resolve(__dirname, 'index.html')
        // }),
        new webpack.HotModuleReplacementPlugin(),
    ]
};
