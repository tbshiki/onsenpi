<?php
/**
 * Custom post type registration.
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Handles registration of custom post type and meta fields.
 */
class WP_Follow_Timeline_CPT {
    /**
     * Post type slug.
     *
     * @var string
     */
    const POST_TYPE = 'wp_follow_item';

    /**
     * Constructor.
     */
    public function __construct() {
        add_action( 'init', array( $this, 'register_post_type' ) );
        add_action( 'init', array( $this, 'register_meta_fields' ) );
    }

    /**
     * Register custom post type for follow items.
     */
    public function register_post_type() {
        $labels = array(
            'name'               => __( 'Follow Items', 'wp-follow-timeline' ),
            'singular_name'      => __( 'Follow Item', 'wp-follow-timeline' ),
            'add_new'            => __( 'Add New', 'wp-follow-timeline' ),
            'add_new_item'       => __( 'Add New Follow Item', 'wp-follow-timeline' ),
            'edit_item'          => __( 'Edit Follow Item', 'wp-follow-timeline' ),
            'new_item'           => __( 'New Follow Item', 'wp-follow-timeline' ),
            'all_items'          => __( 'Follow Items', 'wp-follow-timeline' ),
            'view_item'          => __( 'View Follow Item', 'wp-follow-timeline' ),
            'search_items'       => __( 'Search Follow Items', 'wp-follow-timeline' ),
            'not_found'          => __( 'No follow items found', 'wp-follow-timeline' ),
            'not_found_in_trash' => __( 'No follow items found in Trash', 'wp-follow-timeline' ),
            'menu_name'          => __( 'Follow Timeline', 'wp-follow-timeline' ),
        );

        $args = array(
            'labels'       => $labels,
            'public'       => false,
            'show_ui'      => false,
            'supports'     => array( 'title', 'editor', 'excerpt', 'thumbnail' ),
            'has_archive'  => false,
            'rewrite'      => false,
            'show_in_rest' => false,
        );

        register_post_type( self::POST_TYPE, $args );
    }

    /**
     * Register meta fields for follow items.
     */
    public function register_meta_fields() {
        $meta_keys = array(
            'origin_site_name',
            'origin_site_url',
            'origin_post_url',
            'origin_post_date',
            'origin_post_thumbnail',
            'origin_post_excerpt',
            'origin_post_raw',
        );

        foreach ( $meta_keys as $key ) {
            register_post_meta(
                self::POST_TYPE,
                $key,
                array(
                    'show_in_rest' => false,
                    'single'       => true,
                    'type'         => 'string',
                )
            );
        }
    }
}
