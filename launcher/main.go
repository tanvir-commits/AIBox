// PrivateAI Box — Windows launcher: verify Docker, start Compose, open browser.
// Place PrivateAIBox.exe in the repo root (next to docker-compose.yml).
package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"time"
)

const (
	webURL    = "http://localhost:3000"
	healthURL = "http://localhost:8000/health"
)

func main() {
	if len(os.Args) > 1 && (os.Args[1] == "-stop" || os.Args[1] == "--stop") {
		os.Exit(runStop())
	}
	os.Exit(runStart())
}

func projectRoot() (string, error) {
	exe, err := os.Executable()
	if err != nil {
		return "", err
	}
	root := filepath.Dir(exe)
	if _, err := os.Stat(filepath.Join(root, "docker-compose.yml")); err != nil {
		return "", fmt.Errorf(
			"docker-compose.yml not found next to %s\n\nPut PrivateAIBox.exe in the AIBox repo root (same folder as docker-compose.yml).",
			exe,
		)
	}
	return root, nil
}

func runStart() int {
	if runtime.GOOS != "windows" {
		fmt.Println("This launcher targets Windows. On Mac/Linux use: ./scripts/start.sh --build")
		return 1
	}

	root, err := projectRoot()
	if err != nil {
		fmt.Println("Error:", err)
		pause()
		return 1
	}

	if err := checkDocker(); err != nil {
		fmt.Println(err)
		pause()
		return 1
	}

	envPath := filepath.Join(root, ".env")
	examplePath := filepath.Join(root, ".env.example")
	if _, err := os.Stat(envPath); os.IsNotExist(err) {
		if err := copyFile(examplePath, envPath); err != nil {
			fmt.Println("Could not create .env:", err)
			pause()
			return 1
		}
		fmt.Println("Created .env from .env.example")
	}

	fmt.Println("Pulling images one at a time, then starting Local AI Box…")
	fmt.Println("First run can take 10–20 min and needs ~8 GB RAM for Docker.")
	fmt.Println("If the PC freezes, see SHARE_WITH_FRIENDS.txt (safe pull steps).")
	pullErr := composePullSequential(root)
	if pullErr != nil {
		fmt.Println()
		fmt.Println("Pull from GHCR failed (common cause: container packages still private).")
		fmt.Println("  Fix: github.com/users/tanvir-commits/packages → aibox-backend & aibox-web → Public")
		fmt.Println("  Falling back to local build — this will take longer…")
		fmt.Println()
		if err := composeUpBuild(root); err != nil {
			fmt.Println("Failed to build/start stack:", err)
			pause()
			return 1
		}
	} else if err := composeUp(root); err != nil {
		fmt.Println("Failed to start stack:", err)
		pause()
		return 1
	}

	fmt.Println("Waiting for API health…")
	if !waitHealthy(3 * time.Minute) {
		fmt.Println("Health check timed out. Logs: docker compose logs")
		fmt.Println("Try: docker compose ps")
		pause()
		return 1
	}

	fmt.Println("Opening", webURL)
	openBrowser(webURL)
	fmt.Println()
	fmt.Println("Sign in: admin@example.com / changeme")
	fmt.Println("Stop stack: PrivateAIBox.exe -stop   (or: docker compose down)")
	fmt.Println()
	pause()
	return 0
}

func runStop() int {
	root, err := projectRoot()
	if err != nil {
		fmt.Println("Error:", err)
		pause()
		return 1
	}
	if err := checkDocker(); err != nil {
		fmt.Println(err)
		pause()
		return 1
	}
	fmt.Println("Stopping PrivateAI Box…")
	if err := composeDown(root); err != nil {
		fmt.Println(err)
		pause()
		return 1
	}
	fmt.Println("Stopped.")
	pause()
	return 0
}

func checkDocker() error {
	if _, err := exec.LookPath("docker"); err != nil {
		return fmt.Errorf(`Docker was not found in PATH.

Install Docker Desktop for Windows, start it, then run this launcher again:
  https://docs.docker.com/desktop/setup/install/windows-install/

Use WSL 2 backend (Docker Desktop default).`)
	}
	if out, err := exec.Command("docker", "compose", "version").CombinedOutput(); err != nil {
		return fmt.Errorf("docker compose is not available:\n%s\n\nUpdate Docker Desktop.", string(out))
	}
	if out, err := exec.Command("docker", "info").CombinedOutput(); err != nil {
		return fmt.Errorf(`Docker is installed but not running (or not permitted).

Start Docker Desktop and wait until the engine is running, then try again.
%s`, string(out))
	}
	return nil
}

func composePullSequential(root string) error {
	services := []string{"postgres", "qdrant", "backend", "web"}
	var firstErr error
	for _, svc := range services {
		fmt.Println("── pull", svc, "──")
		cmd := exec.Command("docker", "compose", "pull", svc)
		cmd.Dir = root
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		if err := cmd.Run(); err != nil && firstErr == nil {
			firstErr = err
		}
	}
	return firstErr
}

func composeUp(root string) error {
	cmd := exec.Command("docker", "compose", "up", "-d")
	cmd.Dir = root
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

func composeUpBuild(root string) error {
	cmd := exec.Command(
		"docker", "compose",
		"-f", "docker-compose.yml",
		"-f", "docker-compose.dev.yml",
		"up", "-d", "--build",
	)
	cmd.Dir = root
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

func composeDown(root string) error {
	cmd := exec.Command("docker", "compose", "down")
	cmd.Dir = root
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

func waitHealthy(timeout time.Duration) bool {
	deadline := time.Now().Add(timeout)
	client := &http.Client{Timeout: 3 * time.Second}
	for time.Now().Before(deadline) {
		resp, err := client.Get(healthURL)
		if err == nil {
			_, _ = io.Copy(io.Discard, resp.Body)
			resp.Body.Close()
			if resp.StatusCode == http.StatusOK {
				return true
			}
		}
		time.Sleep(2 * time.Second)
	}
	return false
}

func openBrowser(url string) {
	_ = exec.Command("cmd", "/c", "start", "", url).Start()
}

func copyFile(src, dst string) error {
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()
	out, err := os.Create(dst)
	if err != nil {
		return err
	}
	defer out.Close()
	_, err = io.Copy(out, in)
	return err
}

func pause() {
	fmt.Print("Press Enter to close…")
	_, _ = fmt.Scanln()
}
