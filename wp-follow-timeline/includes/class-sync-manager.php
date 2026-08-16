<?php
/**
 * Synchronization manager.
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Handles scheduled sync.
 */
class WP_Follow_Timeline_Sync_Manager {
    /**
     * Settings handler.
     *
     * @var WP_Follow_Timeline_Admin_Settings
     */
    private $settings;

    /**
     * REST fetcher.
     *
     * @var WP_Follow_Timeline_Fetch_REST
     */
    private $rest_fetcher;

    /**
     * RSS fetcher.
     *
     * @var WP_Follow_Timeline_Fetch_RSS
     */
    private $rss_fetcher;

    /**
     * Constructor.
     *
     * @param WP_Follow_Timeline_Admin_Settings $settings Settings handler.
     */
    public function __construct( WP_Follow_Timeline_Admin_Settings $settings ) {
        $this->settings     = $settings;
        $this->rest_fetcher = new WP_Follow_Timeline_Fetch_REST();
        $this->rss_fetcher  = new WP_Follow_Timeline_Fetch_RSS();

        add_action( 'wp_follow_timeline_sync', array( $this, 'run_sync' ) );
    }

    /**
     * Ensure cron event is registered.
     */
    public function register_cron() {
        if ( ! wp_next_scheduled( 'wp_follow_timeline_sync' ) ) {
            wp_schedule_event( time(), 'hourly', 'wp_follow_timeline_sync' );
        }
    }

    /**
     * Run sync job.
     */
    public function run_sync() {
        $sites = $this->settings->get_sites();
        if ( empty( $sites ) ) {
            return;
        }

        foreach ( $sites as $site ) {
            $posts = $this->rest_fetcher->fetch_posts( $site['rest_api_url'] );
            if ( empty( $posts ) ) {
                $posts = $this->rss_fetcher->fetch_posts( $site['rss_url'] );
            }

            $this->store_posts( $posts, $site );
        }
    }

    /**
     * Store fetched posts locally.
     *
     * @param array $posts Posts to store.
     * @param array $site  Site data.
     */
    private function store_posts( $posts, $site ) {
        foreach ( $posts as $post ) {
            if ( empty( $post['link'] ) || $this->post_exists( $post['link'] ) ) {
                continue;
            }

            $post_id = wp_insert_post(
                array(
                    'post_type'   => WP_Follow_Timeline_CPT::POST_TYPE,
                    'post_title'  => $post['title'],
                    'post_status' => 'publish',
                    'post_date'   => $post['date'],
                    'post_content'=> $post['content'],
                    'post_excerpt'=> $post['excerpt'],
                )
            );

            if ( is_wp_error( $post_id ) ) {
                error_log( 'WP Follow Timeline: failed to insert post - ' . $post['link'] );
                continue;
            }

            update_post_meta( $post_id, 'origin_site_name', $site['site_name'] );
            update_post_meta( $post_id, 'origin_site_url', $site['site_url'] );
            update_post_meta( $post_id, 'origin_post_url', $post['link'] );
            update_post_meta( $post_id, 'origin_post_date', $post['date'] );
            update_post_meta( $post_id, 'origin_post_thumbnail', $post['thumbnail'] );
            update_post_meta( $post_id, 'origin_post_excerpt', $post['excerpt'] );
            update_post_meta( $post_id, 'origin_post_raw', $post['content'] );
        }
    }

    /**
     * Determine if post already stored.
     *
     * @param string $url Post URL.
     * @return bool
     */
    private function post_exists( $url ) {
        $query = new WP_Query(
            array(
                'post_type'      => WP_Follow_Timeline_CPT::POST_TYPE,
                'posts_per_page' => 1,
                'meta_query'     => array(
                    array(
                        'key'   => 'origin_post_url',
                        'value' => esc_url_raw( $url ),
                    ),
                ),
            )
        );

        $found = ! empty( $query->posts );

        wp_reset_postdata();

        return $found;
    }
}
