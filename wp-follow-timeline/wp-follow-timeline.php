<?php
/**
 * Plugin Name: WP Follow Timeline
 * Description: Follow multiple WordPress sites and display their posts in a combined timeline.
 * Version: 0.1.0
 * Author: onsenpi
 * License: GPL2+
 * Text Domain: wp-follow-timeline
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

if ( ! class_exists( 'WP_Follow_Timeline' ) ) {
    /**
     * Main plugin class.
     */
    class WP_Follow_Timeline {
        /**
         * Plugin version.
         *
         * @var string
         */
        const VERSION = '0.1.0';

        /**
         * Singleton instance.
         *
         * @var WP_Follow_Timeline|null
         */
        protected static $instance = null;

        /**
         * Get singleton instance.
         *
         * @return WP_Follow_Timeline
         */
        public static function instance() {
            if ( null === self::$instance ) {
                self::$instance = new self();
            }

            return self::$instance;
        }

        /**
         * Constructor.
         */
        private function __construct() {
            $this->define_constants();
            $this->includes();
            $this->hooks();
        }

        /**
         * Define plugin constants.
         */
        private function define_constants() {
            define( 'WP_FOLLOW_TIMELINE_VERSION', self::VERSION );
            define( 'WP_FOLLOW_TIMELINE_PATH', plugin_dir_path( __FILE__ ) );
            define( 'WP_FOLLOW_TIMELINE_URL', plugin_dir_url( __FILE__ ) );
            define( 'WP_FOLLOW_TIMELINE_BASENAME', plugin_basename( __FILE__ ) );
        }

        /**
         * Load required files.
         */
        private function includes() {
            require_once WP_FOLLOW_TIMELINE_PATH . 'includes/class-cpt.php';
            require_once WP_FOLLOW_TIMELINE_PATH . 'includes/class-fetch-rest.php';
            require_once WP_FOLLOW_TIMELINE_PATH . 'includes/class-fetch-rss.php';
            require_once WP_FOLLOW_TIMELINE_PATH . 'includes/class-sync-manager.php';
            require_once WP_FOLLOW_TIMELINE_PATH . 'includes/class-timeline.php';
            require_once WP_FOLLOW_TIMELINE_PATH . 'admin/class-admin-settings.php';
            require_once WP_FOLLOW_TIMELINE_PATH . 'admin/class-admin-menu.php';
        }

        /**
         * Register hooks.
         */
        private function hooks() {
            register_activation_hook( __FILE__, array( $this, 'activate' ) );
            register_deactivation_hook( __FILE__, array( $this, 'deactivate' ) );

            add_action( 'plugins_loaded', array( $this, 'init_plugin' ) );
        }

        /**
         * Initialize plugin components.
         */
        public function init_plugin() {
            new WP_Follow_Timeline_CPT();
            $settings = new WP_Follow_Timeline_Admin_Settings();

            new WP_Follow_Timeline_Admin_Menu( $settings );
            $sync_manager = new WP_Follow_Timeline_Sync_Manager( $settings );
            new WP_Follow_Timeline_Timeline();

            add_action( 'init', array( $sync_manager, 'register_cron' ) );
        }

        /**
         * Plugin activation callback.
         */
        public function activate() {
            $this->init_plugin();
            $timestamp = wp_next_scheduled( 'wp_follow_timeline_sync' );
            if ( false === $timestamp ) {
                wp_schedule_event( time(), 'hourly', 'wp_follow_timeline_sync' );
            }
        }

        /**
         * Plugin deactivation callback.
         */
        public function deactivate() {
            wp_clear_scheduled_hook( 'wp_follow_timeline_sync' );
        }
    }
}

WP_Follow_Timeline::instance();
