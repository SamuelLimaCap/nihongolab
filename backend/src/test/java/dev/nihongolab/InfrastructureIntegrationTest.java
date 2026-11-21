package dev.nihongolab;

import static org.assertj.core.api.Assertions.assertThat;


import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.simple.JdbcClient;

class InfrastructureIntegrationTest extends IntegrationTest {

    @Autowired
    JdbcClient jdbc;

    @Autowired
    TestRestTemplate rest;

    @Test
    void appliesOutboxMigration() {
        Integer applied = jdbc.sql(
                "select count(*) from flyway_schema_history where script = 'V001__shared_event_publication.sql' and success"
                )
            .query(Integer.class).single();
        
        String table = jdbc.sql("select to_regclass('public.event_publication')::text")
            .query(String.class).single();

        assertThat(applied).isEqualTo(1);
        assertThat(table).isEqualTo("event_publication");
    }

    @Test
    void healthIsOpenAndEverythingElseIs401() {
        ResponseEntity<String> health = rest.getForEntity("/actuator/health", String.class);
        assertThat(health.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(health.getBody()).contains("\"status\":\"UP\"");

        ResponseEntity<String> api = rest.getForEntity("/api/qualquer-coisa", String.class);
        assertThat(api.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
        assertThat(api.getHeaders().getFirst("WWW-Authenticate")).isNull();
    }
    
}
