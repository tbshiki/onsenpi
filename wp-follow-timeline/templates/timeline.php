<?php
/**
 * Default timeline template.
 *
 * @var WP_Post[] $posts Posts to render.
 */
?>
<div class="wp-follow-timeline">
    <?php if ( ! empty( $posts ) ) : ?>
        <?php foreach ( $posts as $post ) : ?>
            <?php
            $site_name  = get_post_meta( $post->ID, 'origin_site_name', true );
            $site_url   = get_post_meta( $post->ID, 'origin_site_url', true );
            $post_url   = get_post_meta( $post->ID, 'origin_post_url', true );
            $thumbnail  = get_post_meta( $post->ID, 'origin_post_thumbnail', true );
            $excerpt    = get_post_meta( $post->ID, 'origin_post_excerpt', true );
            $post_date  = get_post_meta( $post->ID, 'origin_post_date', true );
            ?>
            <article class="wp-follow-timeline__item">
                <header>
                    <?php if ( $site_name ) : ?>
                        <span class="wp-follow-timeline__site"><a href="<?php echo esc_url( $site_url ); ?>" target="_blank" rel="noopener noreferrer"><?php echo esc_html( $site_name ); ?></a></span>
                    <?php endif; ?>
                    <h2 class="wp-follow-timeline__title"><a href="<?php echo esc_url( $post_url ); ?>" target="_blank" rel="noopener noreferrer"><?php echo esc_html( get_the_title( $post ) ); ?></a></h2>
                    <?php if ( $post_date ) : ?>
                        <time class="wp-follow-timeline__date" datetime="<?php echo esc_attr( $post_date ); ?>"><?php echo esc_html( date_i18n( get_option( 'date_format' ), strtotime( $post_date ) ) ); ?></time>
                    <?php endif; ?>
                </header>

                <?php if ( $thumbnail ) : ?>
                    <div class="wp-follow-timeline__thumbnail">
                        <a href="<?php echo esc_url( $post_url ); ?>" target="_blank" rel="noopener noreferrer">
                            <img src="<?php echo esc_url( $thumbnail ); ?>" alt="" loading="lazy" />
                        </a>
                    </div>
                <?php endif; ?>

                <div class="wp-follow-timeline__excerpt">
                    <p><?php echo esc_html( $excerpt ? $excerpt : wp_trim_words( wp_strip_all_tags( $post->post_content ), 40 ) ); ?></p>
                </div>
                <p><a class="button" href="<?php echo esc_url( $post_url ); ?>" target="_blank" rel="noopener noreferrer"><?php esc_html_e( 'Read more', 'wp-follow-timeline' ); ?></a></p>
            </article>
        <?php endforeach; ?>
    <?php else : ?>
        <p><?php esc_html_e( 'No posts found.', 'wp-follow-timeline' ); ?></p>
    <?php endif; ?>
</div>
