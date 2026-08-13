package com.earningssentiment.service;

import com.earningssentiment.exception.BadRequestException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;

@Service
public class FileStorageService {
    private static final Set<String> SUPPORTED_EXTENSIONS = Set.of(".txt", ".pdf");
    private final Path uploadDirectory;

    public FileStorageService(@Value("${app.upload-dir}") String uploadDirectory) {
        this.uploadDirectory = Path.of(uploadDirectory).toAbsolutePath().normalize();
        try {
            Files.createDirectories(this.uploadDirectory);
        } catch (IOException exception) {
            throw new IllegalStateException("Could not create upload directory", exception);
        }
    }

    public Path store(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new BadRequestException("A non-empty transcript file is required");
        }
        String originalName = file.getOriginalFilename() == null ? "" : file.getOriginalFilename();
        String lowerName = originalName.toLowerCase(Locale.ROOT);
        String extension = SUPPORTED_EXTENSIONS.stream()
                .filter(lowerName::endsWith)
                .findFirst()
                .orElseThrow(() -> new BadRequestException("Only .txt and .pdf transcript files are supported"));
        if (originalName.length() == extension.length()) {
            throw new BadRequestException("The transcript file must have a name before its extension");
        }

        Path target = uploadDirectory.resolve(UUID.randomUUID() + extension).normalize();
        if (!target.startsWith(uploadDirectory)) {
            throw new BadRequestException("Invalid file name");
        }
        try {
            Files.copy(file.getInputStream(), target, StandardCopyOption.REPLACE_EXISTING);
            return target;
        } catch (IOException exception) {
            throw new IllegalStateException("Could not store transcript file", exception);
        }
    }

    public void deleteQuietly(Path path) {
        try {
            Files.deleteIfExists(path);
        } catch (IOException ignored) {
            // A failed cleanup should not hide the original upload error.
        }
    }
}
