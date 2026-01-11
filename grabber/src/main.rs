#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::{env::var_os, path::PathBuf};
use active_win_pos_rs::{ActiveWindow, get_active_window};
use chrono::{DateTime, Local, NaiveDateTime, TimeZone};
use std::fs::{OpenOptions, metadata};
use std::io;
use std::io::{BufRead, Write};
use std::thread;
use std::time::{Duration, Instant};

const APPDATA_FOLDER_NAME: &str = "Program-Using-Logger";
const UPDATE_SPEED: u64 = 1000;
const HEADER: &str = "name,time";
const HEARTBEAT_FORMART: &str = "%H:%M:%S %d_%m_%Y";

fn get_base_path() -> String {
    format!("{}\\{}", var_os("APPDATA").map(PathBuf::from).expect("No APPDATA directory").display(),
    APPDATA_FOLDER_NAME)
}

fn write(activity_name: &str, time: DateTime<Local>) {
    let month_year = time.format("%m_%Y").to_string();
    let day_month_year = time.format("%d_%m_%Y").to_string();
    let log_folder_path = format!("{}\\{}", &get_base_path() , &month_year);

    match std::fs::create_dir(&log_folder_path) {
        Ok(()) => {println!("Dirrectory {} for log storaging is created", &log_folder_path)},
        _ => {}
    }

    let path_to_log = format!("{}\\{}.csv", &log_folder_path, &day_month_year);

    if metadata(&path_to_log).is_err() {
        let mut file = OpenOptions::new()
            .write(true)
            .create(true)
            .open(&path_to_log)
            .unwrap();
        file.write_all(HEADER.as_bytes()).unwrap();
    }

    let mut file = OpenOptions::new()
        .create(false)
        .write(true)
        .append(true)
        .open(&path_to_log)
        .unwrap();

    let new_record = format!("{},{}", &activity_name, time.format("%H:%M:%S"));

    println!("Writing record: {}", new_record);

    let _ = file.write(format!("\n{}", &new_record).as_bytes()).unwrap();
}

fn read_last_line(path: &str) -> io::Result<String> {
    let file = OpenOptions::new().read(true).open(path)?;
    let reader = io::BufReader::new(file);

    reader
        .lines()
        .filter_map(Result::ok)
        .last()
        .ok_or_else(|| io::Error::new(io::ErrorKind::Other, "File is empty"))
}

fn write_heartbeat() {
    let now = Local::now();
    let mut file = OpenOptions::new()
        .create(true)
        .write(true)
        .append(false)
        .open(format!("{}\\heartbeat.lock", &get_base_path() ))
        .unwrap();
    file.write_all(format!("{}", now.format(HEARTBEAT_FORMART)).as_bytes())
        .ok();
}

fn read_heartbeat() -> Option<DateTime<Local>> {
    if let Ok(last_line) = read_last_line(&format!("{}\\heartbeat.lock", &get_base_path() )) {
        if let Ok(naive_dt) = NaiveDateTime::parse_from_str(&last_line, HEARTBEAT_FORMART) {
            return Some(Local.from_local_datetime(&naive_dt).unwrap());
        }
    }
    None
}

fn check_log_heartbeat(datetime: &DateTime<Local>) {
    let log_date = datetime.format("%d_%m_%Y").to_string();
    let path_to_log = format!(
        "{}\\{}\\{}.csv",
        get_base_path() ,
        datetime.format("%m_%Y").to_string(),
        log_date
    );
    println!("Checking heartbeat for {}", path_to_log);

    if let Some(heartbeat_datetime) = read_heartbeat() {
        if let Ok(last_record) = read_last_line(&path_to_log) {
            if last_record.contains("Heartbeat") || last_record.contains(HEADER) {
                return;
            }
        }
        write("Heartbeat End", heartbeat_datetime);
    };
}

fn main() {
    let interval = Duration::from_millis(UPDATE_SPEED);
    let mut next_tick = Instant::now();

    let mut last_window: Option<ActiveWindow> = None;
    let mut now = Local::now();

    println!(
        "============ START OF PROGRAM ({}) ============",
        now.format("%H:%M:%S")
    );
    
    match std::fs::create_dir(&get_base_path()) {
        Ok(()) => {println!("Dirrectory {} for log storaging is created", &get_base_path())},
        Err(err) => {println!("Can't create dirrectory at {} ({err})", &get_base_path())}
    }

    println!(
        "Logs will be writed in: {}\\{}\\{}.csv",
        get_base_path() ,
        now.format("%m_%Y").to_string(),
        now.format("%d_%m_%Y").to_string()
    );

    if let Some(heartbeat_datetime) = read_heartbeat() {
        check_log_heartbeat(&heartbeat_datetime);
    }

    loop {
        write_heartbeat();

        if let Ok(current_window) = get_active_window() {
            now = Local::now();
            if let Some(window) = &last_window {
                if !window.app_name.contains(&current_window.app_name) {
                    write(&current_window.app_name, now);
                    last_window = Some(current_window);
                }
            } else {
                write(&current_window.app_name, now);
                last_window = Some(current_window);
            }
        }

        next_tick += interval;
        let now = Instant::now();
        if next_tick > now {
            thread::sleep(next_tick - now);
        }
    }
}
