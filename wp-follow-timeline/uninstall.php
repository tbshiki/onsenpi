<?php
/**
 * Uninstall cleanup.
 */

if ( ! defined( 'WP_UNINSTALL_PLUGIN' ) ) {
    exit;
}

$option_key = 'wp_follow_timeline_sites';
$posts      = get_posts(
    array(
        'post_type'      => 'wp_follow_item',
        'posts_per_page' => -1,
        'fields'         => 'ids',
    )
);

if ( ! empty( $posts ) ) {
    foreach ( $posts as $post_id ) {
        wp_delete_post( $post_id, true );
    }
}

delete_option( $option_key );
