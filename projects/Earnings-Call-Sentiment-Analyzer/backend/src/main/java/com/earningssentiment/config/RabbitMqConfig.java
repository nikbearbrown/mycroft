package com.earningssentiment.config;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.DirectExchange;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMqConfig {
    public static final String EXCHANGE = "sentiment.exchange";
    public static final String QUEUE = "sentiment.analysis.queue";
    public static final String ROUTING_KEY = "sentiment.analysis";

    @Bean
    DirectExchange sentimentExchange() {
        return new DirectExchange(EXCHANGE, true, false);
    }

    @Bean
    Queue sentimentQueue() {
        return new Queue(QUEUE, true);
    }

    @Bean
    Binding sentimentBinding(Queue sentimentQueue, DirectExchange sentimentExchange) {
        return BindingBuilder.bind(sentimentQueue).to(sentimentExchange).with(ROUTING_KEY);
    }

    @Bean
    MessageConverter jsonMessageConverter() {
        return new Jackson2JsonMessageConverter();
    }
}
