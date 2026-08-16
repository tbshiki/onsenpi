<?php
/**
 * Admin settings for followed sites.
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Handles option storage for followed sites.
 */
class WP_Follow_Timeline_Admin_Settings {
    /**
     * Option name.
     *
     * @var string
     */
    const OPTION_KEY = 'wp_follow_timeline_sites';

    /**
     * Get all registered sites.
     *
     * @return array
     */
    public function get_sites() {
        $sites = get_option( self::OPTION_KEY, array() );

        return is_array( $sites ) ? $sites : array();
    }

    /**
     * Save a site configuration.
     *
     * @param array $data Site data.
     */
    public function save_site( $data ) {
        $sites = $this->get_sites();
        $id    = isset( $data['id'] ) ? sanitize_text_field( $data['id'] ) : uniqid( 'site_', true );

        $sites[ $id ] = array(
            'id'           => $id,
            'site_name'    => sanitize_text_field( $data['site_name'] ?? '' ),
            'site_url'     => esc_url_raw( $data['site_url'] ?? '' ),
            'rest_api_url' => esc_url_raw( $data['rest_api_url'] ?? '' ),
            'rss_url'      => esc_url_raw( $data['rss_url'] ?? '' ),
            'notes'        => sanitize_text_field( $data['notes'] ?? '' ),
        );

        update_option( self::OPTION_KEY, $sites );
    }

    /**
     * Delete a site configuration.
     *
     * @param string $id Site ID.
     */
    public function delete_site( $id ) {
        $sites = $this->get_sites();
        if ( isset( $sites[ $id ] ) ) {
            unset( $sites[ $id ] );
            update_option( self::OPTION_KEY, $sites );
        }
    }
}
