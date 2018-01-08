extern crate env_logger;
#[macro_use]
extern crate log;

// FFI
extern crate libc;

use std::fs::File;
use std::io::prelude::*;
use std::io::{BufReader, Lines};

// FFI
use std::ptr;
use libc::c_char;
use std::ffi::{CStr, CString};

type CorpyResult<T> = Result<T, String>;

pub struct Vertical {
    lines: Lines<BufReader<File>>,
}

impl Vertical {
    pub fn new(path: &str) -> CorpyResult<Self> {
        match File::open(path) {
            Ok(file) => Ok(Vertical {
                lines: BufReader::new(file).lines(),
            }),
            Err(e) => Err(e.to_string()),
        }
    }

    pub fn next_line(&mut self) -> Option<CorpyResult<String>> {
        match self.lines.next() {
            Some(value) => match value {
                Ok(line) => Some(Ok(line)),
                Err(e) => Some(Err(e.to_string())),
            },
            None => None,
        }
    }
}

#[no_mangle]
pub extern "C" fn init_logger() {
    env_logger::init();
}

#[no_mangle]
pub extern "C" fn string_free(string: *mut c_char) {
    if string.is_null() {
        return;
    }
    debug!("Deallocating string");
    unsafe {
        CString::from_raw(string);
    }
}

#[no_mangle]
pub extern "C" fn vertical_new(path: *const c_char) -> *mut Vertical {
    let path = unsafe {
        assert!(!path.is_null());
        CStr::from_ptr(path)
    };
    let path = path.to_str().unwrap();
    match Vertical::new(path) {
        Ok(vertical) => {
            debug!("Allocating Vertical {:?}", path);
            Box::into_raw(Box::new(vertical))
        }
        Err(e) => {
            error!("Error in native code while opening {:?}: {}", path, e);
            ptr::null_mut()
        }
    }
}

#[no_mangle]
pub extern "C" fn vertical_free(ptr: *mut Vertical) {
    if ptr.is_null() {
        return;
    }
    debug!("Deallocating Vertical");
    unsafe {
        Box::from_raw(ptr);
    }
}

#[no_mangle]
pub extern "C" fn vertical_next_line(ptr: *mut Vertical) -> *const c_char {
    let vertical = unsafe {
        assert!(!ptr.is_null());
        &mut *ptr
    };
    match vertical.next_line() {
        Some(value) => match value {
            Ok(line) => {
                debug!("Allocating string {:?}", line);
                CString::new(line).unwrap().into_raw()
            }
            Err(e) => {
                error!(
                    "Error in native code while reading next Vertical line: {}",
                    e
                );
                ptr::null()
            }
        },
        None => ptr::null(),
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
