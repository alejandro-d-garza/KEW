use serde::{Deserialize, Serialize};
use std::{env, fs, path::PathBuf};

#[derive(Debug, Deserialize, Serialize)]
struct QueueState {
    person_count: u32,
    queue_time_seconds: f64,
    updated_at: f64,
}

/// Resolve the detector state path for development and deployed overrides.
fn state_path() -> PathBuf {
    env::var_os("KEW_STATE_PATH")
        .map(PathBuf::from)
        .unwrap_or_else(|| {
            PathBuf::from(env!("CARGO_MANIFEST_DIR"))
                .parent()
                .expect("src-tauri must be inside the project")
                .join("runtime/queue_state.json")
        })
}

/// Return the detector's most recent atomic state snapshot.
#[tauri::command]
fn read_queue_state() -> Result<QueueState, String> {
    let contents = fs::read_to_string(state_path()).map_err(|error| error.to_string())?;
    serde_json::from_str(&contents).map_err(|error| error.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![read_queue_state])
        .run(tauri::generate_context!())
        .expect("error while running Kew");
}

#[cfg(test)]
mod tests {
    use super::QueueState;

    #[test]
    fn parses_python_state_contract() {
        let state: QueueState =
            serde_json::from_str(r#"{"person_count":3,"queue_time_seconds":90,"updated_at":1}"#)
                .expect("valid state");
        assert_eq!(state.person_count, 3);
    }
}
