package dev.nihongolab;
import java.time.Clock;
import java.time.ZoneOffset;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableAsync
public class NihongolabApplication {
    public static void main(String[] args) {
        SpringApplication.run(NihongolabApplication.class, args);
    }

    @Bean
    Clock clock() {
        return Clock.tickMillis(ZoneOffset.UTC);
    }
}
