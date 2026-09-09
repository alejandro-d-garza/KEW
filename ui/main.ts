import { invoke } from "@tauri-apps/api/core";

interface QueueState {
  person_count: number;
  queue_time_seconds: number;
  updated_at: number;
}

const waitElement = document.querySelector<HTMLElement>("#wait");
const peopleElement = document.querySelector<HTMLElement>("#people");
const statusElement = document.querySelector<HTMLElement>("#status");

/** Render the newest queue state returned by the native shell. */
async function renderState(): Promise<void> {
  if (!waitElement || !peopleElement || !statusElement) return;
  try {
    const state = await invoke<QueueState>("read_queue_state");
    const minutes = Math.ceil(state.queue_time_seconds / 60);
    waitElement.textContent = `${minutes} min estimated wait`;
    peopleElement.textContent = `${state.person_count} people detected in the queue`;
    statusElement.textContent = state.updated_at > 0 ? "Live" : "Waiting for detector data";
  } catch (error) {
    statusElement.textContent = `Detector unavailable: ${String(error)}`;
  }
}

void renderState();
window.setInterval(() => void renderState(), 1000);
