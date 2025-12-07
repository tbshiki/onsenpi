<?php
/**
 * Timeline shortcode.
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Shortcode handler for timeline.
 */
class WP_Follow_Timeline_Timeline {
    /**
     * Constructor.
     */
    public function __construct() {
        add_shortcode( 'wp_follow_timeline', array( $this, 'render_timeline' ) );
    }

    /**
     * Render timeline shortcode.
     *
     * @return string
     */
    public function render_timeline() {
        $posts = get_posts(
            array(
                'post_type'      => WP_Follow_Timeline_CPT::POST_TYPE,
                'posts_per_page' => 20,
                'post_status'    => 'publish',
                'orderby'        => 'date',
                'order'          => 'DESC',
            )
        );

        $template = locate_template( 'wp-follow-timeline/timeline.php' );
        if ( ! $template ) {
            $template = WP_FOLLOW_TIMELINE_PATH . 'templates/timeline.php';
        }

        ob_start();
        include $template;

        return ob_get_clean();
    }
}
