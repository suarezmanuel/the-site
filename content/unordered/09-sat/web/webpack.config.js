const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  // 1. MODE: 'development' for easy debugging, 'production' for optimized code
  mode: 'development',

  // 2. ENTRY: The starting point of our application
  entry: './src/index.js',

  // 3. OUTPUT: Where Webpack should place the final bundled file
  output: {
    // The final filename will be 'main.js'
    filename: 'main.js',
    // It will be placed in a folder named 'dist' in the project root
    path: path.resolve(__dirname, 'dist'),
    // Clean the output directory before each build
    clean: true,
  },

  // 4. PLUGINS: Tools that extend Webpack's functionality
  plugins: [
    new HtmlWebpackPlugin({
      // This tells the plugin to use our src/index.html as a template
      template: './src/index.html',
    }),
  ],

  // 5. DEV SERVER: Configuration for the live-reloading server
  devServer: {
    // Tell the server to serve files from the 'dist' directory
    static: './dist',
    // Open the browser automatically when the server starts
    open: true,
  },


  module: {
    rules: [
        {
            test: /\.css$/i,
            use: ['style-loader', 'css-loader'],
        },
    ],
  },
};