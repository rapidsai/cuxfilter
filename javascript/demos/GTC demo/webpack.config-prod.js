const path = require("path");
const webpack = require("webpack");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const HtmlWebpackPlugin = require('html-webpack-plugin');
const dotenv = require('dotenv').config({path:'/usr/src/app/config.env'});

console.log(dotenv.parsed);

module.exports = {
    entry: path.resolve(__dirname, "src/index.jsx"),
    mode: "production",
    node: {
        fs: 'empty' // https://github.com/webpack-contrib/css-loader/issues/447 *shrug*
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: "styles.css",
            chunkFilename: "[id].styles.css"
        }),
        new HtmlWebpackPlugin({
          title: 'RAPIDS Viz Demo',
          favicon: './src/favicon.png',
          template: './src/index-template.html',
          inject: true
        }),
        new webpack.DefinePlugin({
          'process.env.REACT_APP_server_ip': JSON.stringify(process.env.server_ip),
          'process.env.REACT_APP_demo_dataset_name': JSON.stringify(process.env.demo_dataset_name),
          'process.env.REACT_APP_demo_mapbox_token': JSON.stringify(process.env.demo_mapbox_token)
        })
    ],
    optimization: {
        // for minicssextractpluin to put into single file
        splitChunks: {
            cacheGroups: {
                styles: {
                    name: 'styles',
                    test: /\.css$/,
                    chunks: 'all',
                    minSize: 300000 // keeping size large for simplicity
                }
            }
        }
    },
    module: {
        rules: [{
                test: /\.(js|jsx)$/,
                exclude: /(node_modules)/,
                include: [path.resolve(__dirname)],
                loader: "babel-loader",
                options: { presets: ['env', 'react'] }
            },
            {
                test: /\.(css|scss)$/,
                use: [{
                        loader: MiniCssExtractPlugin.loader
                    },
                    {
                        loader: "css-loader",

                    }, {
                        loader: "sass-loader",
                    }
                ]
            },
            {
                test: /\.(png|jpg|gif|svg)$/,
                use: [{
                    loader: "file-loader",
                    options: { name: "./img/[name].[ext]" }
                }]
            }
        ]
    },
    resolve: {
        extensions: [".js", ".jsx", ".css", ".scss"]
    },
    output: {
        path: path.resolve(__dirname, "public"),
        publicPath: "./",
        filename: "bundle.js"
    }
}
