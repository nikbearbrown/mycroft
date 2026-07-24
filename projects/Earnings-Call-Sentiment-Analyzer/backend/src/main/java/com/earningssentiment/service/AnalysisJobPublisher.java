package com.earningssentiment.service;

import com.earningssentiment.config.RabbitMqConfig;
import com.earningssentiment.dto.AnalysisJobQueuedEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.event.TransactionPhase;
import org.springframework.transaction.event.TransactionalEventListener;

@Service
public class AnalysisJobPublisher {
    private static final Logger LOGGER = LoggerFactory.getLogger(AnalysisJobPublisher.class);
    private static final long CONFIRM_TIMEOUT_MILLIS = 5_000;

    private final RabbitTemplate rabbitTemplate;
    private final JobDispatchFailureService failureService;

    public AnalysisJobPublisher(RabbitTemplate rabbitTemplate, JobDispatchFailureService failureService) {
        this.rabbitTemplate = rabbitTemplate;
        this.failureService = failureService;
    }

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onQueued(AnalysisJobQueuedEvent event) {
        try {
            rabbitTemplate.invoke(operations -> {
                operations.convertAndSend(
                        RabbitMqConfig.EXCHANGE, RabbitMqConfig.ROUTING_KEY, event.message());
                operations.waitForConfirmsOrDie(CONFIRM_TIMEOUT_MILLIS);
                return null;
            });
        } catch (RuntimeException exception) {
            LOGGER.error("Could not dispatch analysis job {}", event.message().jobId(), exception);
            failureService.markFailed(event.message().jobId(), event.message().transcriptId(), exception.getMessage());
        }
    }
}
