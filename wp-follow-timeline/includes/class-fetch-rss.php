<?php
/**
 * RSS/Atom fetcher.
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Fetch posts from RSS/Atom feeds.
 */
class WP_Follow_Timeline_Fetch_RSS {
    /**
     * Fetch posts from RSS feed.
     *
     * @param string $rss_url Feed URL.
     * @return array
     */
    public function fetch_posts( $rss_url ) {
        if ( empty( $rss_url ) ) {
            return array();
        }

        include_once ABSPATH . WPINC . '/feed.php';
        $feed = fetch_feed( $rss_url );
        if ( is_wp_error( $feed ) ) {
            return array();
        }

        $maxitems = $feed->get_item_quantity( 20 );
        $items    = $feed->get_items( 0, $maxitems );

        $posts = array();
        foreach ( $items as $item ) {
            $posts[] = array(
                'title'     => sanitize_text_field( $item->get_title() ),
                'link'      => esc_url_raw( $item->get_link() ),
                'date'      => $item->get_date( 'c' ),
                'excerpt'   => wp_strip_all_tags( $item->get_description() ),
                'thumbnail' => $this->get_thumbnail_from_item( $item ),
                'content'   => $item->get_content(),
            );
        }

        return $posts;
    }

    /**
     * Try to extract thumbnail URL from feed item.
     *
     * @param SimplePie_Item $item Feed item.
     * @return string
     */
    private function get_thumbnail_from_item( $item ) {
        $enclosure = $item->get_enclosure();
        if ( $enclosure && $enclosure->get_link() ) {
            return esc_url_raw( $enclosure->get_link() );
        }

        $thumbnail = $item->get_item_tags( 'http://search.yahoo.com/mrss/', 'thumbnail' );
        if ( ! empty( $thumbnail[0]['attribs']['']['url'] ) ) {
            return esc_url_raw( $thumbnail[0]['attribs']['']['url'] );
        }

        return '';
    }
}
