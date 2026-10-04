import Foundation
import PDFKit
import AppKit
// macOS-only inspection aid. The LaTeX build does not depend on this script.
let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let output = root.appendingPathComponent("build/extraction")
try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
let files = try FileManager.default.contentsOfDirectory(at: root.appendingPathComponent("pdf-prof"), includingPropertiesForKeys: nil).filter { $0.pathExtension.lowercased() == "pdf" }.sorted { $0.lastPathComponent < $1.lastPathComponent }
for file in files {
    guard let document = PDFDocument(url: file) else { fatalError("Cannot read \(file.path)") }
    let id = String(file.lastPathComponent.prefix(2))
    for index in 0..<document.pageCount {
        let page = document.page(at: index)!
        let stem = String(format: "%@-%03d", id, index + 1)
        let image = page.thumbnail(of: NSSize(width: 1400, height: 1850), for: .mediaBox)
        let bitmap = NSBitmapImageRep(data: image.tiffRepresentation!)!
        try bitmap.representation(using: .png, properties: [:])!.write(to: output.appendingPathComponent(stem + ".png"))
        try (page.string ?? "").write(to: output.appendingPathComponent(stem + ".txt"), atomically: true, encoding: .utf8)
    }
    print("\(file.lastPathComponent): \(document.pageCount) pages")
}
