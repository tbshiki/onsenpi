<?php
/**
 * Admin menu for managing followed sites.
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Adds admin menu pages.
 */
class WP_Follow_Timeline_Admin_Menu {
    /**
     * Settings handler.
     *
     * @var WP_Follow_Timeline_Admin_Settings
     */
    private $settings;

    /**
     * Constructor.
     *
     * @param WP_Follow_Timeline_Admin_Settings $settings Settings handler.
     */
    public function __construct( WP_Follow_Timeline_Admin_Settings $settings ) {
        $this->settings = $settings;
        add_action( 'admin_menu', array( $this, 'register_menu' ) );
        add_action( 'admin_post_wp_follow_timeline_save_site', array( $this, 'handle_save_site' ) );
        add_action( 'admin_post_wp_follow_timeline_delete_site', array( $this, 'handle_delete_site' ) );
    }

    /**
     * Register admin menu page.
     */
    public function register_menu() {
        add_menu_page(
            __( 'Followed Sites', 'wp-follow-timeline' ),
            __( 'Follow Timeline', 'wp-follow-timeline' ),
            'manage_options',
            'wp-follow-timeline',
            array( $this, 'render_page' ),
            'dashicons-rss',
            59
        );
    }

    /**
     * Handle save action from admin form.
     */
    public function handle_save_site() {
        if ( ! current_user_can( 'manage_options' ) ) {
            wp_die( esc_html__( 'You do not have permission to perform this action.', 'wp-follow-timeline' ) );
        }

        check_admin_referer( 'wp_follow_timeline_save_site' );

        $site_url     = sanitize_text_field( wp_unslash( $_POST['site_url'] ?? '' ) );
        $rest_api_url = sanitize_text_field( wp_unslash( $_POST['rest_api_url'] ?? '' ) );
        $rss_url      = sanitize_text_field( wp_unslash( $_POST['rss_url'] ?? '' ) );

        if ( empty( $rest_api_url ) && ! empty( $site_url ) ) {
            $rest_api_url = trailingslashit( $site_url ) . 'wp-json/wp/v2/posts';
        }

        if ( empty( $rss_url ) && ! empty( $site_url ) ) {
            $rss_url = trailingslashit( $site_url ) . 'feed/';
        }

        $this->settings->save_site(
            array(
                'id'           => sanitize_text_field( wp_unslash( $_POST['id'] ?? '' ) ),
                'site_name'    => sanitize_text_field( wp_unslash( $_POST['site_name'] ?? '' ) ),
                'site_url'     => esc_url_raw( $site_url ),
                'rest_api_url' => esc_url_raw( $rest_api_url ),
                'rss_url'      => esc_url_raw( $rss_url ),
                'notes'        => sanitize_text_field( wp_unslash( $_POST['notes'] ?? '' ) ),
            )
        );

        wp_safe_redirect( admin_url( 'admin.php?page=wp-follow-timeline&updated=1' ) );
        exit;
    }

    /**
     * Handle delete action.
     */
    public function handle_delete_site() {
        if ( ! current_user_can( 'manage_options' ) ) {
            wp_die( esc_html__( 'You do not have permission to perform this action.', 'wp-follow-timeline' ) );
        }

        check_admin_referer( 'wp_follow_timeline_delete_site' );

        $id = sanitize_text_field( wp_unslash( $_GET['id'] ?? '' ) );
        if ( $id ) {
            $this->settings->delete_site( $id );
        }

        wp_safe_redirect( admin_url( 'admin.php?page=wp-follow-timeline&deleted=1' ) );
        exit;
    }

    /**
     * Render admin page.
     */
    public function render_page() {
        if ( ! current_user_can( 'manage_options' ) ) {
            return;
        }

        $sites = $this->settings->get_sites();
        ?>
        <div class="wrap">
            <h1><?php esc_html_e( 'Followed Sites', 'wp-follow-timeline' ); ?></h1>
            <?php if ( isset( $_GET['updated'] ) ) : ?>
                <div class="notice notice-success is-dismissible"><p><?php esc_html_e( 'Site saved.', 'wp-follow-timeline' ); ?></p></div>
            <?php endif; ?>
            <?php if ( isset( $_GET['deleted'] ) ) : ?>
                <div class="notice notice-success is-dismissible"><p><?php esc_html_e( 'Site removed.', 'wp-follow-timeline' ); ?></p></div>
            <?php endif; ?>
            <h2 class="title"><?php esc_html_e( 'Sites', 'wp-follow-timeline' ); ?></h2>
            <table class="widefat striped">
                <thead>
                <tr>
                    <th><?php esc_html_e( 'Site Name', 'wp-follow-timeline' ); ?></th>
                    <th><?php esc_html_e( 'URL', 'wp-follow-timeline' ); ?></th>
                    <th><?php esc_html_e( 'REST API URL', 'wp-follow-timeline' ); ?></th>
                    <th><?php esc_html_e( 'RSS URL', 'wp-follow-timeline' ); ?></th>
                    <th><?php esc_html_e( 'Notes', 'wp-follow-timeline' ); ?></th>
                    <th><?php esc_html_e( 'Actions', 'wp-follow-timeline' ); ?></th>
                </tr>
                </thead>
                <tbody>
                <?php if ( ! empty( $sites ) ) : ?>
                    <?php foreach ( $sites as $site ) : ?>
                        <tr>
                            <td><?php echo esc_html( $site['site_name'] ); ?></td>
                            <td><a href="<?php echo esc_url( $site['site_url'] ); ?>" target="_blank" rel="noopener noreferrer"><?php echo esc_html( $site['site_url'] ); ?></a></td>
                            <td><code><?php echo esc_html( $site['rest_api_url'] ); ?></code></td>
                            <td><code><?php echo esc_html( $site['rss_url'] ); ?></code></td>
                            <td><?php echo esc_html( $site['notes'] ); ?></td>
                            <td>
                                <form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>" onsubmit="return confirm('<?php echo esc_js( __( 'Delete this site?', 'wp-follow-timeline' ) ); ?>');">
                                    <?php wp_nonce_field( 'wp_follow_timeline_delete_site' ); ?>
                                    <input type="hidden" name="action" value="wp_follow_timeline_delete_site">
                                    <input type="hidden" name="id" value="<?php echo esc_attr( $site['id'] ); ?>">
                                    <button type="submit" class="button-link delete-link"><?php esc_html_e( 'Delete', 'wp-follow-timeline' ); ?></button>
                                </form>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                <?php else : ?>
                    <tr><td colspan="6"><?php esc_html_e( 'No sites added yet.', 'wp-follow-timeline' ); ?></td></tr>
                <?php endif; ?>
                </tbody>
            </table>

            <h2 class="title" style="margin-top:2em;">
                <?php esc_html_e( 'Add Site', 'wp-follow-timeline' ); ?>
            </h2>
            <form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>" class="wp-follow-timeline-form">
                <?php wp_nonce_field( 'wp_follow_timeline_save_site' ); ?>
                <input type="hidden" name="action" value="wp_follow_timeline_save_site">
                <table class="form-table" role="presentation">
                    <tr>
                        <th scope="row"><label for="site_name"><?php esc_html_e( 'Site Name', 'wp-follow-timeline' ); ?></label></th>
                        <td><input type="text" name="site_name" id="site_name" class="regular-text" required></td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="site_url"><?php esc_html_e( 'Site URL', 'wp-follow-timeline' ); ?></label></th>
                        <td><input type="url" name="site_url" id="site_url" class="regular-text" required placeholder="https://example.com"></td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="rest_api_url"><?php esc_html_e( 'REST API URL', 'wp-follow-timeline' ); ?></label></th>
                        <td><input type="url" name="rest_api_url" id="rest_api_url" class="regular-text" placeholder="https://example.com/wp-json/wp/v2/posts"></td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="rss_url"><?php esc_html_e( 'RSS URL', 'wp-follow-timeline' ); ?></label></th>
                        <td><input type="url" name="rss_url" id="rss_url" class="regular-text" placeholder="https://example.com/feed/"></td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="notes"><?php esc_html_e( 'Notes', 'wp-follow-timeline' ); ?></label></th>
                        <td><input type="text" name="notes" id="notes" class="regular-text"></td>
                    </tr>
                </table>
                <?php submit_button( __( 'Save Site', 'wp-follow-timeline' ) ); ?>
            </form>
        </div>
        <?php
    }
}
