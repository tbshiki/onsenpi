<?php
/**
 * REST API fetcher.
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Fetch posts using REST API.
 */
class WP_Follow_Timeline_Fetch_REST {
    /**
     * Fetch posts from REST endpoint.
     *
     * @param string $rest_api_url REST API endpoint.
     * @return array
     */
    public function fetch_posts( $rest_api_url ) {
        if ( empty( $rest_api_url ) ) {
            return array();
        }

        $endpoint = add_query_arg(
            array(
                'per_page' => 20,
                'orderby'  => 'date',
                'order'    => 'desc',
                '_embed'   => 'true',
            ),
            $rest_api_url
        );

        $response = wp_remote_get( $endpoint, array( 'timeout' => 10 ) );
        if ( is_wp_error( $response ) ) {
            return array();
        }

        $body = wp_remote_retrieve_body( $response );
        $data = json_decode( $body, true );

        if ( empty( $data ) || ! is_array( $data ) ) {
            return array();
        }

        $items = array();
        foreach ( $data as $item ) {
            $items[] = array(
                'title'     => sanitize_text_field( $item['title']['rendered'] ?? '' ),
                'link'      => esc_url_raw( $item['link'] ?? '' ),
                'date'      => sanitize_text_field( $item['date'] ?? '' ),
                'excerpt'   => wp_strip_all_tags( $item['excerpt']['rendered'] ?? '' ),
                'thumbnail' => $this->extract_thumbnail( $item ),
                'content'   => $item['content']['rendered'] ?? '',
            );
        }

        return $items;
    }

    /**
     * Extract thumbnail URL from REST response.
     *
     * @param array $item REST item.
     * @return string
     */
    private function extract_thumbnail( $item ) {
        if ( ! empty( $item['jetpack_featured_media_url'] ) ) {
            return esc_url_raw( $item['jetpack_featured_media_url'] );
        }

        if ( isset( $item['_embedded']['wp:featuredmedia'][0]['source_url'] ) ) {
            return esc_url_raw( $item['_embedded']['wp:featuredmedia'][0]['source_url'] );
        }

        if ( ! empty( $item['featured_media_url'] ) ) {
            return esc_url_raw( $item['featured_media_url'] );
        }

        return '';
    }
}
