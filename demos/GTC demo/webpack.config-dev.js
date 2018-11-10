const path = require("path");
const webpack = require("webpack");

module.exports = {
    entry: path.resolve(__dirname, "src/index.jsx"),
    devtool: "source-map",
    mode: "development",
    node: {
        fs: 'empty' // https://github.com/webpack-contrib/css-loader/issues/447 *shrug*
    },
    module: {
        rules: [{
                test: /\.(js|jsx)$/,
                exclude: /(node_modules)/,
                loader: "babel-loader",
                options: { presets: ['env'] }
            },
            {
                test: /\.(css|scss)$/,
                use: [{
                    loader: "style-loader"
                }, {
                    loader: "css-loader",
                    options: {
                        sourceMap: true
                    }
                }, {
                    loader: "sass-loader",
                    options: {
                        sourceMap: true
                    }
                }]
            },
            {
                test: /\.(png|jpg|gif|svg)$/,
                use: [{
                    loader: "file-loader",
                    options: { name: "[path][name].[ext]" }
                }]
            }
        ]
    },
    resolve: {
        extensions: [".js", ".jsx", ".css", ".scss"]
    },
    output: {
        path: path.resolve(__dirname, "src"),
        publicPath: path.resolve(__dirname, "/"),
        filename: "bundle.js"
    },
    devServer: {
        contentBase: path.join(__dirname, "src/"),
        port: 3000,
        publicPath: "http://localhost:3000/",
        hotOnly: true,
        open: false,

    },
    plugins: [new webpack.HotModuleReplacementPlugin()]
};