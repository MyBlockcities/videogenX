const TerserPlugin = require('terser-webpack-plugin');

module.exports = function override(config, env) {
  if (env === 'production') {
    config.optimization = {
      ...config.optimization,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            parse: {
              ecma: 8,
            },
            compress: {
              ecma: 5,
              warnings: false,
              comparisons: false,
              inline: 2,
              evaluate: false, // Disable eval
            },
            mangle: {
              safari10: true,
            },
            output: {
              ecma: 5,
              comments: false,
              ascii_only: true,
            },
          },
        }),
      ],
    };
  }
  
  return config;
};
